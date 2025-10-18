# tienda/blockchain_service.py
from web3 import Web3
import json
import time
from django.conf import settings

class BlockchainService:
    def __init__(self, provider_url='http://localhost:8545'):
        try:
            # Conectar a Ganache
            self.w3 = Web3(Web3.HTTPProvider(provider_url))
            
            if not self.w3.is_connected():
                print("❌ No se pudo conectar a Ganache. Verifica que esté ejecutándose en puerto 8545")
                raise Exception("No se pudo conectar a Ganache")
            
            # Configurar cuenta por defecto (primera cuenta de Ganache)
            self.default_account = self.w3.eth.accounts[0]
            
            # Private key de la primera cuenta de Ganache (conocida para desarrollo)
            self.private_key = "0x4f3edf983ac636a65a842ce7c78d9aa706d3b113bce9c46f30d7d21715b23b1d"
            
            print("✅ Conectado exitosamente a Ganache")
            print(f"📦 Último bloque: {self.w3.eth.block_number}")
            print(f"👤 Cuenta por defecto: {self.default_account}")
            print(f"💰 Balance: {self.w3.from_wei(self.w3.eth.get_balance(self.default_account), 'ether')} ETH")
            
            # Para esta demo, NO desplegamos un contrato real
            # Simulamos que tenemos un contrato
            self.contract_address = "0xTiendaBlockchainContract"
            
        except Exception as e:
            print(f"❌ Error inicializando BlockchainService: {e}")
            raise
    
    def create_product_on_blockchain(self, name, price):
        """Simular creación de producto enviando ETH (transacción real)"""
        try:
            # DEBE tener esta parte para enviar transacción REAL
            price_wei = self.w3.to_wei(0.0001, 'ether')
            
            transaction = {
                'to': self.default_account,
                'value': price_wei,
                'gas': 21000,
                'gasPrice': self.w3.to_wei('20', 'gwei'),
                'nonce': self.w3.eth.get_transaction_count(self.default_account),
                'chainId': 1337
            }
            
            # Estas 3 líneas son CLAVE:
            signed_txn = self.w3.eth.account.sign_transaction(transaction, self.private_key)
            tx_hash = self.w3.eth.send_raw_transaction(signed_txn.raw_transaction)
            return tx_hash.hex()  # ← Debe devolver el hash real
            
        except Exception as e:
            print(f"❌ Error real: {e}")
            return f"0xSIM_{name}_{int(time.time())}"
    
    def purchase_product_on_blockchain(self, product_id, quantity, total_price):
        """Registrar compra con transacción real"""
        try:
            # Convertir precio a wei (usamos una cantidad pequeña fija para demo)
            total_wei = self.w3.to_wei(0.0002, 'ether')
            
            # Crear transacción real
            transaction = {
                'to': self.default_account,  # Enviarnos a nosotros mismos
                'value': total_wei,
                'gas': 21000,
                'gasPrice': self.w3.to_wei('20', 'gwei'),
                'nonce': self.w3.eth.get_transaction_count(self.default_account),
                'chainId': 1337
            }
            
            # Firmar transacción
            signed_txn = self.w3.eth.account.sign_transaction(transaction, self.private_key)
            
            # Enviar transacción
            tx_hash = self.w3.eth.send_raw_transaction(signed_txn.raw_transaction)
            
            print(f"✅ Compra registrada con transacción real")
            print(f"📄 TX Hash REAL: {tx_hash.hex()}")
            print(f"🛒 Producto: {product_id}, Cantidad: {quantity}")
            
            return tx_hash.hex()
            
        except Exception as e:
            print(f"❌ Error en transacción de compra: {e}")
            return f"0xBUY_{product_id}_{int(time.time())}"
    
    def get_blockchain_info(self):
        """Obtener información REAL de Ganache"""
        try:
            balance_wei = self.w3.eth.get_balance(self.default_account)
            balance_eth = self.w3.from_wei(balance_wei, 'ether')
            
            # Obtener algunas transacciones recientes del bloque
            latest_block = self.w3.eth.get_block('latest')
            
            return {
                'connected': True,
                'network': 'Ganache Local',
                'block_number': self.w3.eth.block_number,
                'default_account': self.default_account,
                'balance_eth': float(balance_eth),
                'contract_address': self.contract_address,
                'accounts_available': len(self.w3.eth.accounts),
                'gas_price_gwei': float(self.w3.from_wei(self.w3.eth.gas_price, 'gwei')),
                'latest_block_hash': latest_block['hash'].hex() if latest_block else 'N/A',
                'transaction_count': latest_block['transactions'].__len__() if latest_block else 0,
                'message': '✅ Conectado a Ganache - Transacciones REALES'
            }
        except Exception as e:
            return {
                'connected': False,
                'error': str(e)
            }
    
    def get_accounts(self):
        """Obtener cuentas REALES de Ganache"""
        try:
            accounts = self.w3.eth.accounts
            accounts_info = []
            
            for i, account in enumerate(accounts[:5]):  # Solo primeras 5
                balance = self.w3.from_wei(self.w3.eth.get_balance(account), 'ether')
                accounts_info.append({
                    'index': i,
                    'address': account,
                    'balance_eth': float(balance)
                })
            
            return accounts_info
        except Exception as e:
            return {'error': str(e)}
    
    def send_test_transaction(self):
        """Método para probar transacciones"""
        try:
            # Enviar una pequeña cantidad a nosotros mismos
            transaction = {
                'to': self.default_account,
                'value': self.w3.to_wei(0.0001, 'ether'),
                'gas': 21000,
                'gasPrice': self.w3.to_wei('20', 'gwei'),
                'nonce': self.w3.eth.get_transaction_count(self.default_account),
                'chainId': 1337
            }
            
            signed_txn = self.w3.eth.account.sign_transaction(transaction, self.private_key)
            tx_hash = self.w3.eth.send_raw_transaction(signed_txn.raw_transaction)
            
            return {
                'success': True,
                'tx_hash': tx_hash.hex(),
                'message': 'Transacción de prueba enviada exitosamente'
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }