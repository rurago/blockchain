# apps/blockchain/blockchain_service.py
from web3 import Web3
import json
import os
from django.conf import settings

class BlockchainService:
    def __init__(self, network="localhost"):
        self.network = network
        self.setup_connection()
        
    def setup_connection(self):
        """Configurar conexión según la red"""
        if self.network == "localhost":
            self.web3 = Web3(Web3.HTTPProvider('http://127.0.0.1:8545'))
            self.contract_address = "0x5FbDB2315678afecb367f032d93F642f64180aa3"  # Reemplaza con tu dirección
        elif self.network == "sepolia":
            self.web3 = Web3(Web3.HTTPProvider(settings.ALCHEMY_API_URL))
            self.contract_address = settings.CONTRACT_ADDRESS_SEPOLIA
        
        # Cargar ABI del contrato
        with open('blockchain/artifacts/contracts/ECommerce.sol/ECommerce.json', 'r') as f:
            contract_data = json.load(f)
            self.contract_abi = contract_data['abi']
        
        self.contract = self.web3.eth.contract(
            address=self.contract_address,
            abi=self.contract_abi
        )
    
    def check_connection(self):
        """Verificar conexión con la blockchain"""
        try:
            connected = self.web3.is_connected()
            block_number = self.web3.eth.block_number if connected else 0
            return connected, f"Conectado a {self.network} - Block: {block_number}"
        except Exception as e:
            return False, f"Error de conexión: {str(e)}"
    
    def register_product(self, name, price, stock):
        """Registrar nuevo producto en blockchain"""
        try:
            if not self.web3.is_connected():
                return {'success': False, 'error': 'No hay conexión con la blockchain'}
            
            # Usar la primera cuenta de Hardhat para testing
            account = self.web3.eth.accounts[0]
            
            # Preparar transacción
            transaction = self.contract.functions.registerProduct(
                name, price, stock
            ).build_transaction({
                'from': account,
                'gas': 200000,
                'gasPrice': self.web3.eth.gas_price,
                'nonce': self.web3.eth.get_transaction_count(account)
            })
            
            # Firmar transacción (en local no necesita clave privada)
            signed_txn = self.web3.eth.account.sign_transaction(
                transaction, '0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80'  # Private key de Hardhat
            )
            
            # Enviar transacción
            tx_hash = self.web3.eth.send_raw_transaction(signed_txn.rawTransaction)
            
            # Esperar confirmación
            receipt = self.web3.eth.wait_for_transaction_receipt(tx_hash)
            
            return {
                'success': True,
                'tx_hash': tx_hash.hex(),
                'block_number': receipt.blockNumber,
                'product_id': None  # Se obtendría del evento
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def purchase_product(self, product_id, quantity, product_data, buyer_address):
        """Realizar compra en blockchain"""
        try:
            if not self.web3.is_connected():
                return {'success': False, 'error': 'No hay conexión con la blockchain'}
            
            # Obtener información del producto
            product_info = self.contract.functions.getProduct(product_id).call()
            product_price = product_info[2]  # price está en posición 2
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
            
            # Firmar transacción
            signed_txn = self.web3.eth.account.sign_transaction(
                transaction, '0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80'
            )
            
            # Enviar transacción
            tx_hash = self.web3.eth.send_raw_transaction(signed_txn.rawTransaction)
            
            # Esperar confirmación
            receipt = self.web3.eth.wait_for_transaction_receipt(tx_hash)
            
            return {
                'success': True,
                'tx_hash': tx_hash.hex(),
                'block_number': receipt.blockNumber,
                'total_price': total_price
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
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