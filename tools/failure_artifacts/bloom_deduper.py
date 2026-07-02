# -*- coding: utf-8 -*-
"""
分布式 BloomFilter 去重模块
Bloom Filter Deduplication

特性:
- 纯 Python 实现 (bytearray 模拟 bit array)，零外部依赖
- 接口设计为 Redis-compatible，可无缝替换为 Redis BF
- 支持 false positive rate 配置与统计
- 自动计算最优 bit_count 和 hash_count

理论背景:
  给定期望容量 n 和误报率 p:
    bit_count  m = -n * ln(p) / (ln2)^2
    hash_count k = (m/n) * ln2
"""
from __future__ import annotations

import hashlib
import math
from typing import Any


# ─────────────────────────────────────────────────────────────────────────
# 最优参数计算
# ─────────────────────────────────────────────────────────────────────────

def optimal_bloom_params(capacity: int, fpr: float) -> tuple[int, int]:
    """
    计算 BloomFilter 的最优 bit 数和哈希函数数。
    
    Args:
        capacity: 预期插入元素数量
        fpr: 期望的误报率 (e.g. 0.001 = 0.1%)
    
    Returns:
        (bit_count, hash_count)
    """
    if capacity <= 0:
        capacity = 1
    fpr = max(1e-10, min(fpr, 0.5))
    # m = -n * ln(p) / (ln2)^2
    bit_count = int(math.ceil(-capacity * math.log(fpr) / (math.log(2) ** 2)))
    # k = (m/n) * ln2
    hash_count = int(math.ceil((bit_count / capacity) * math.log(2)))
    return max(bit_count, 64), max(hash_count, 1)


# ─────────────────────────────────────────────────────────────────────────
# 核心 BloomFilter
# ─────────────────────────────────────────────────────────────────────────

class BloomFilter:
    """
    纯 Python BloomFilter 实现，使用 bytearray 模拟 bit array。
    多哈希函数通过 SHA-256 分段派生，避免重复导入多个库。
    """

    def __init__(self, capacity: int = 100_000, false_positive_rate: float = 0.001):
        """
        Args:
            capacity: 预期最大插入元素数
            false_positive_rate: 可接受的误报率 (0.0~1.0)
        """
        self.capacity = capacity
        self.target_fpr = false_positive_rate
        self.bit_count, self.hash_count = optimal_bloom_params(capacity, false_positive_rate)
        # bytearray 作为 bit array (每个字节存 8 bit)
        self._byte_count = (self.bit_count + 7) // 8
        self._bits = bytearray(self._byte_count)
        self._inserted = 0

    def _get_bit_positions(self, item: str) -> list[int]:
        """用 SHA-256 分段派生 hash_count 个 bit 位置，模拟多哈希函数。"""
        # 生成足够多的哈希字节
        positions = []
        seed = 0
        while len(positions) < self.hash_count:
            h = hashlib.sha256(f"{seed}:{item}".encode("utf-8")).digest()
            # 每4字节取一个 uint32
            for i in range(0, len(h) - 3, 4):
                val = int.from_bytes(h[i:i+4], "big")
                positions.append(val % self.bit_count)
                if len(positions) >= self.hash_count:
                    break
            seed += 1
        return positions[:self.hash_count]

    def _set_bit(self, pos: int) -> None:
        self._bits[pos >> 3] |= (1 << (pos & 7))

    def _get_bit(self, pos: int) -> bool:
        return bool(self._bits[pos >> 3] & (1 << (pos & 7)))

    def add(self, item: str) -> None:
        """将元素加入 BloomFilter。"""
        for pos in self._get_bit_positions(item):
            self._set_bit(pos)
        self._inserted += 1

    def contains(self, item: str) -> bool:
        """检查元素是否可能存在 (有误报率，无漏报)。"""
        return all(self._get_bit(pos) for pos in self._get_bit_positions(item))

    def is_probably_duplicate(self, item: str) -> bool:
        """
        一步完成去重: 检查是否已存在，若否则加入。
        Returns True 表示 item 可能已存在 (duplicate)。
        """
        if self.contains(item):
            return True   # 已存在 (可能是误报)
        self.add(item)
        return False      # 确定不存在，已加入

    @property
    def fill_ratio(self) -> float:
        """当前 bit array 填充率 (越高误报率越高)。"""
        bits_set = sum(bin(b).count("1") for b in self._bits)
        return bits_set / self.bit_count

    def estimated_fpr(self) -> float:
        """当前实际估算误报率: (fill_ratio)^hash_count。"""
        fr = self.fill_ratio
        return fr ** self.hash_count

    def stats(self) -> dict[str, Any]:
        """返回完整统计信息。"""
        return {
            "capacity": self.capacity,
            "inserted": self._inserted,
            "bit_count": self.bit_count,
            "hash_count": self.hash_count,
            "fill_ratio": round(self.fill_ratio, 6),
            "estimated_fpr": round(self.estimated_fpr(), 8),
            "target_fpr": self.target_fpr,
            "memory_bytes": self._byte_count,
            "unique_estimated": self._inserted,
        }


# ─────────────────────────────────────────────────────────────────────────
# BloomDedupeChecker (兼容 DedupeChecker 接口)
# ─────────────────────────────────────────────────────────────────────────

class BloomDedupeChecker:
    """
    基于 BloomFilter 的去重检测器，接口兼容 DedupeChecker。
    
    优势:
    - 内存效率: 100万条记录仅需约 2MB (vs 内存 set 约 50MB+)
    - 速度: O(k) 哈希计算，k 通常为 7~10
    - 可扩展: 接口与 RedisBloomAdapter 完全一致，可无缝切换
    
    缺陷:
    - 有误报率 (默认 0.1%): 极少数非重复记录会被误判为重复
    - 不支持删除元素
    """

    def __init__(
        self,
        key_fields: list[str],
        capacity: int = 1_000_000,
        fpr: float = 0.001
    ):
        self.key_fields = key_fields
        self._bloom = BloomFilter(capacity=capacity, false_positive_rate=fpr)
        self.duplicate_count = 0
        self.total_seen = 0

    def compute_key(self, record: dict) -> str:
        """构建去重复合键。"""
        parts = [str(record.get(f, "")) for f in self.key_fields]
        return "|".join(parts)

    def is_duplicate(self, record: dict) -> bool:
        """检测是否为重复记录。"""
        key = self.compute_key(record)
        self.total_seen += 1
        if self._bloom.is_probably_duplicate(key):
            self.duplicate_count += 1
            return True
        return False

    def report(self) -> dict[str, Any]:
        """返回去重统计报告。"""
        return {
            "unique_seen": self._bloom._inserted,
            "duplicates_found": self.duplicate_count,
            "total_seen": self.total_seen,
            "bloom_stats": self._bloom.stats(),
            "backend": "BloomFilter (pure-python)",
        }


# ─────────────────────────────────────────────────────────────────────────
# RedisBloomAdapter (Stub for production)
# ─────────────────────────────────────────────────────────────────────────

class RedisBloomAdapter:
    """
    Redis BloomFilter 适配器 (接口占位，供生产环境接入 Redis BF 使用)。
    
    生产接入方法:
        pip install redis
        r = redis.Redis(host='localhost', port=6379)
        r.execute_command('BF.RESERVE', 'dedup:urls', 0.001, 1000000)
        # 然后用 BF.ADD / BF.EXISTS 替代本类方法
    """

    def __init__(self, key_fields: list[str], redis_url: str = "redis://localhost:6379", **kwargs):
        self.key_fields = key_fields
        self.redis_url = redis_url

    def _raise_error(self):
        raise NotImplementedError(
            "RedisBloomAdapter requires a running Redis instance with RedisBloom module.\n"
            "Install: pip install redis\n"
            "Start:   docker run -p 6379:6379 redislabs/rebloom\n"
            "Then replace this adapter with actual redis.Redis() calls:\n"
            "  r.execute_command('BF.RESERVE', 'dedup:urls', 0.001, 1_000_000)\n"
            "  r.execute_command('BF.ADD', 'dedup:urls', key)\n"
            "  r.execute_command('BF.EXISTS', 'dedup:urls', key)\n"
            "For now, use BloomDedupeChecker (pure-Python) instead."
        )

    def compute_key(self, record: dict) -> str:
        self._raise_error()

    def is_duplicate(self, record: dict) -> bool:
        self._raise_error()

    def report(self) -> dict:
        self._raise_error()
        raise NotImplementedError
