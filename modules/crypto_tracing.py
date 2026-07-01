"""
Cryptocurrency Tracing Module
Bitcoin/Ethereum transaction analysis, wallet tracking, blockchain forensics.
"""

import requests
import re
import time
import json
from typing import Dict, List, Optional
from .base import OSINTModule, ModuleResult


class CryptoTracing(OSINTModule):
    """Cryptocurrency transaction tracing and blockchain forensics."""

    name = "crypto_tracing"
    description = "Cryptocurrency transaction tracing - BTC/ETH wallet analysis, blockchain forensics"

    # Public blockchain API endpoints (no API key required for basic queries)
    BLOCKCHAIN_APIS = {
        "bitcoin": {
            "address_info": "https://blockchain.info/rawaddr/{address}",
            "tx_info": "https://blockchain.info/rawtx/{txid}",
            "latest_block": "https://blockchain.info/latestblock",
        },
        "ethereum": {
            "address_info": "https://api.etherscan.io/api?module=account&action=txlist&address={address}&sort=desc",
            "balance": "https://api.etherscan.io/api?module=account&action=balance&address={address}&tag=latest",
            "tx_info": "https://api.etherscan.io/api?module=proxy&action=eth_getTransactionByHash&txhash={txid}",
        },
    }

    # Crypto address regex patterns
    PATTERNS = {
        "btc": re.compile(r"\b[13][a-km-zA-HJ-NP-Z1-9]{25,34}\b"),
        "eth": re.compile(r"\b0x[a-fA-F0-9]{40}\b"),
        "ltc": re.compile(r"\b[LM3][a-km-zA-HJ-NP-Z1-9]{26,33}\b"),
        "xrp": re.compile(r"\br[1-9A-HJ-NP-Za-km-z]{25,34}\b"),
        "bch": re.compile(r"\b(bitcoincash:)?(q|p)[a-z0-9]{41}\b"),
    }

    def __init__(self, config: Optional[Dict] = None):
        super().__init__(config)
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "OmniSightAI-CryptoIntel/2.0",
        })

    def _detect_addresses(self, text: str) -> Dict[str, List[str]]:
        """Extract cryptocurrency addresses from text."""
        found = {}
        for currency, pattern in self.PATTERNS.items():
            matches = pattern.findall(text)
            if matches:
                found[currency] = list(set(matches))
        return found

    def _trace_bitcoin(self, address: str) -> Dict:
        """Trace a Bitcoin address."""
        result = {"address": address, "transactions": [], "balance": "unknown", "total_received": "unknown"}

        try:
            resp = self.session.get(
                self.BLOCKCHAIN_APIS["bitcoin"]["address_info"].format(address=address),
                timeout=15,
            )
            if resp.status_code == 200:
                data = resp.json()
                result["balance"] = data.get("final_balance", 0) / 1e8  # satoshi to BTC
                result["total_received"] = data.get("total_received", 0) / 1e8
                result["total_sent"] = data.get("total_sent", 0) / 1e8
                result["tx_count"] = data.get("n_tx", 0)

                # Get recent transactions
                txs = data.get("txs", [])[:10]
                for tx in txs:
                    result["transactions"].append({
                        "txid": tx.get("hash", ""),
                        "time": tx.get("time", 0),
                        "total_btc": tx.get("out", [{}])[0].get("value", 0) / 1e8 if tx.get("out") else 0,
                        "inputs": len(tx.get("inputs", [])),
                        "outputs": len(tx.get("out", [])),
                    })
        except Exception as e:
            result["error"] = str(e)[:100]

        return result

    def _trace_ethereum(self, address: str) -> Dict:
        """Trace an Ethereum address."""
        result = {"address": address, "transactions": [], "balance": "unknown"}

        try:
            # Get balance
            bal_resp = self.session.get(
                self.BLOCKCHAIN_APIS["ethereum"]["balance"].format(address=address),
                timeout=10,
            )
            if bal_resp.status_code == 200:
                bal_data = bal_resp.json()
                if bal_data.get("status") == "1":
                    result["balance"] = int(bal_data.get("result", 0)) / 1e18  # wei to ETH

            # Get transactions
            tx_resp = self.session.get(
                self.BLOCKCHAIN_APIS["ethereum"]["address_info"].format(address=address),
                timeout=10,
            )
            if tx_resp.status_code == 200:
                tx_data = tx_resp.json()
                if tx_data.get("status") == "1":
                    txs = tx_data.get("result", [])[:10]
                    result["tx_count"] = len(txs)
                    for tx in txs:
                        result["transactions"].append({
                            "txid": tx.get("hash", ""),
                            "block": tx.get("blockNumber", ""),
                            "from": tx.get("from", ""),
                            "to": tx.get("to", ""),
                            "value_eth": int(tx.get("value", 0)) / 1e18,
                            "time": tx.get("timeStamp", 0),
                        })
        except Exception as e:
            result["error"] = str(e)[:100]

        return result

    def execute(self, target: str, **kwargs) -> ModuleResult:
        """
        Execute crypto tracing.
        Target can be a crypto address (BTC/ETH) or a domain/username to search for addresses.
        """
        start = time.time()

        results = {
            "target": target,
            "detected_addresses": {},
            "bitcoin_analysis": [],
            "ethereum_analysis": [],
            "risk_indicators": [],
        }

        # Check if target is itself a crypto address
        is_btc = bool(re.match(r"^[13][a-km-zA-HJ-NP-Z1-9]{25,34}$", target))
        is_eth = bool(re.match(r"^0x[a-fA-F0-9]{40}$", target))

        if is_btc:
            results["detected_addresses"] = {"btc": [target]}
            btc_result = self._trace_bitcoin(target)
            results["bitcoin_analysis"].append(btc_result)
            results["risk_indicators"].append("Direct BTC address analyzed")

        elif is_eth:
            results["detected_addresses"] = {"eth": [target]}
            eth_result = self._trace_ethereum(target)
            results["ethereum_analysis"].append(eth_result)
            results["risk_indicators"].append("Direct ETH address analyzed")

        else:
            # Search for addresses related to the target
            results["note"] = (
                "Target is not a direct crypto address. "
                "Use a BTC or ETH address for direct blockchain tracing."
            )

        duration = (time.time() - start) * 1000
        return self._success(results, duration)
