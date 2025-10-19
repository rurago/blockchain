# apps/blockchain/alchemy_integration.py
from web3 import Web3
import json
import os
from django.conf import settings

class BlockchainService:
    def __init__(self):
        self.web3 = Web3(Web3.HTTPProvider(settings.ALCHEMY_API_URL))
        self.contract_address = settings.CONTRACT_ADDRESS
        self.contract_abi = self._load_abi()
        self.contract = self.web3.eth.contract(
            address=self.contract_address,
            abi=self.contract_abi
        )
        self.owner_private_key = settings.OWNER_PRIVATE_KEY
        self.owner_address = settings.OWNER_ADDRESS

    def _load_abi(self):
        """Cargar ABI del contrato desde el archivo de compilación"""
        try:
            with open('build/contracts/ECommerce.json', 'r') as f:
                contract_data = json.load(f)
                return contract_data['abi']
        except FileNotFoundError:
            # ABI básico como fallback
            return [
                {
                    "inputs": [],
                    "stateMutability": "nonpayable",
                    "type": "constructor"
                },
                {
                    "anonymous": False,
                    "inputs": [
                        {
                            "indexed": True,
                            "internalType": "uint256",
                            "name": "productId",
                            "type": "uint256"
                        },
                        {
                            "indexed": False,
                            "internalType": "string",
                            "name": "name",
                            "type": "string"
                        },
                        {
                            "indexed": False,
                            "internalType": "uint256",
                            "name": "price",
                            "type": "uint256"
                        },
                        {
                            "indexed": False,
                            "internalType": "uint256",
                            "name": "stock",
                            "type": "uint256"
                        },
                        {
                            "indexed": False,
                            "internalType": "address",
                            "name": "creator",
                            "type": "address"
                        }
                    ],
                    "name": "ProductRegistered",
                    "type": "event"
                }
            ]

    def check_connection(self):
        """Verificar conexión con Sepolia"""
        try:
            if self.web3.is_connected():
                block_number = self.web3.eth.block_number
                return True, f"Conectado a Sepolia - Block: {block_number}"
            else:
                return False, "No conectado a la red"
        except Exception as e:
            return False, f"Error de conexión: {str(e)}"

    def register_product(self, name, price, stock):
        """Registrar nuevo producto en blockchain"""
        try:
            # Preparar transacción
            transaction = self.contract.functions.registerProduct(
                name, price, stock
            ).build_transaction({
                'from': self.owner_address,
                'gas': 200000,
                'gasPrice': self.web3.eth.gas_price,
                'nonce': self.web3.eth.get_transaction_count(self.owner_address)
            })

            # Firmar transacción
            signed_txn = self.web3.eth.account.sign_transaction(
                transaction, self.owner_private_key
            )

            # Enviar transacción
            tx_hash = self.web3.eth.send_raw_transaction(signed_txn.rawTransaction)
            
            # Esperar confirmación
            receipt = self.web3.eth.wait_for_transaction_receipt(tx_hash)
            
            return {
                'success': True,
                'tx_hash': tx_hash.hex(),
                'product_id': None,  # Se obtendría del evento
                'block_number': receipt.blockNumber
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    def register_purchase(self, product_id, quantity, product_data, buyer_address):
        """Registrar compra en blockchain"""
        try:
            # Obtener precio del producto
            product = self.contract.functions.getProduct(product_id).call()
            product_price = product[2]  # price está en la posición 2
            total_price = product_price * quantity

            # Preparar transacción
            transaction = self.contract.functions.purchaseProduct(
                product_id, quantity, json.dumps(product_data)
            ).build_transaction({
                'from': buyer_address,
                'value': total_price,
                'gas': 300000,
                'gasPrice': self.web3.eth.gas_price,
                'nonce': self.web3.eth.get_transaction_count(buyer_address)
            })

            # Firmar transacción (en un caso real, el usuario firmaría)
            # Para demo, usamos una cuenta controlada
            signed_txn = self.web3.eth.account.sign_transaction(
                transaction, self.owner_private_key
            )

            # Enviar transacción
            tx_hash = self.web3.eth.send_raw_transaction(signed_txn.rawTransaction)
            
            # Esperar confirmación
            receipt = self.web3.eth.wait_for_transaction_receipt(tx_hash)
            
            return {
                'success': True,
                'tx_hash': tx_hash.hex(),
                'purchase_id': None,  # Se obtendría del evento
                'block_number': receipt.blockNumber
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    def get_product(self, product_id):
        """Obtener información de producto desde blockchain"""
        try:
            product = self.contract.functions.getProduct(product_id).call()
            return {
                'id': product[0],
                'name': product[1],
                'price': product[2],
                'stock': product[3],
                'creator': product[4],
                'created_at': product[5]
            }
        except Exception as e:
            return {'error': str(e)}

    def get_purchase(self, purchase_id):
        """Obtener información de compra desde blockchain"""
        try:
            purchase = self.contract.functions.getPurchase(purchase_id).call()
            return {
                'purchase_id': purchase[0],
                'product_id': purchase[1],
                'buyer': purchase[2],
                'quantity': purchase[3],
                'total_price': purchase[4],
                'purchased_at': purchase[5],
                'product_data': purchase[6]
            }
        except Exception as e:
            return {'error': str(e)}