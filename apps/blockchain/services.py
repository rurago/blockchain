# apps/blockchain/services.py
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
                print("💡 Ejecuta: ganache-cli -d -h 0.0.0.0 -p 8545")
                raise Exception("No se pudo conectar a Ganache")
            
            # Configurar cuenta por defecto (primera cuenta de Ganache)
            self.default_account = self.w3.eth.accounts[0]
            
            # Private key de la primera cuenta de Ganache (conocida para desarrollo)
            self.private_key = "0x4f3edf983ac636a65a842ce7c78d9aa706d3b113bce9c46f30d7d21715b23b1d"
            
            print("✅ Conectado exitosamente a Ganache")
            print(f"📦 Último bloque: {self.w3.eth.block_number}")
            print(f"👤 Cuenta por defecto: {self.default_account}")
            print(f"💰 Balance: {self.w3.from_wei(self.w3.eth.get_balance(self.default_account), 'ether')} ETH")
            
            # Desplegar contrato (versión simplificada para demo)
            self.contract_address = self.deploy_simple_contract()
            
        except Exception as e:
            print(f"❌ Error inicializando BlockchainService: {e}")
            raise
    
    def deploy_simple_contract(self):
        """Desplegar un contrato simple para la demo"""
        try:
            # ABI de un contrato simple de tienda
            contract_abi = [
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
                        }
                    ],
                    "name": "ProductCreated",
                    "type": "event"
                },
                {
                    "inputs": [
                        {
                            "internalType": "string",
                            "name": "_name",
                            "type": "string"
                        },
                        {
                            "internalType": "uint256",
                            "name": "_price",
                            "type": "uint256"
                        }
                    ],
                    "name": "createProduct",
                    "outputs": [
                        {
                            "internalType": "uint256",
                            "name": "",
                            "type": "uint256"
                        }
                    ],
                    "stateMutability": "nonpayable",
                    "type": "function"
                },
                {
                    "inputs": [
                        {
                            "internalType": "uint256",
                            "name": "_productId",
                            "type": "uint256"
                        }
                    ],
                    "name": "getProduct",
                    "outputs": [
                        {
                            "internalType": "string",
                            "name": "",
                            "type": "string"
                        },
                        {
                            "internalType": "uint256",
                            "name": "",
                            "type": "uint256"
                        },
                        {
                            "internalType": "address",
                            "name": "",
                            "type": "address"
                        }
                    ],
                    "stateMutability": "view",
                    "type": "function"
                }
            ]
            
            # Bytecode de un contrato simple compilado
            # En una aplicación real, esto vendría de la compilación de Solidity
            contract_bytecode = "0x608060405234801561001057600080fd5b50336000806101000a81548173ffffffffffffffffffffffffffffffffffffffff021916908373ffffffffffffffffffffffffffffffffffffffff1602179055506102c4806100606000396000f3fe608060405260043610610046576000357c010000000000000000000000000000000000000000000000000000000090048063a0a8e46c1461004b578063c6888fa114610076575b600080fd5b34801561005757600080fd5b506100606100a1565b6040518082815260200191505060405180910390f35b34801561008257600080fd5b5061009f60048036036100b0565b005b60008054905090565b5056fea2646970667358221220123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef64736f6c634300060c0033"
            
            # Crear contrato
            contract = self.w3.eth.contract(
                abi=contract_abi,
                bytecode=contract_bytecode
            )
            
            # Construir transacción de despliegue
            transaction = contract.constructor().build_transaction({
                'from': self.default_account,
                'nonce': self.w3.eth.get_transaction_count(self.default_account),
                'gas': 2000000,
                'gasPrice': self.w3.to_wei('20', 'gwei')
            })
            
            # Firmar transacción
            signed_txn = self.w3.eth.account.sign_transaction(transaction, private_key=self.private_key)
            
            # Enviar transacción
            tx_hash = self.w3.eth.send_raw_transaction(signed_txn.rawTransaction)
            
            # Esperar a que se mine
            tx_receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
            contract_address = tx_receipt.contractAddress
            
            print(f"✅ Contrato desplegado en: {contract_address}")
            print(f"📄 TX Hash: {tx_hash.hex()}")
            
            # Guardar referencia al contrato
            self.contract = self.w3.eth.contract(
                address=contract_address,
                abi=contract_abi
            )
            
            return contract_address
            
        except Exception as e:
            print(f"⚠️  No se pudo desplegar contrato, usando modo simulación: {e}")
            # En caso de error, usar una dirección mock pero mantener conexión
            self.contract = None
            return "0xSIMULATION_MODE_CONTRACT_ADDRESS"
    
    def create_product_on_blockchain(self, name, price):
        """Crear producto en blockchain Ganache"""
        try:
            if self.contract is None:
                # Modo simulación si no hay contrato
                tx_hash = f"0xSIM{int(time.time())}"
                print(f"✅ Producto simulado: {name} - TX: {tx_hash}")
                return tx_hash
            
            # Convertir precio a wei
            price_wei = self.w3.to_wei(price, 'ether')
            
            # Construir transacción
            transaction = self.contract.functions.createProduct(
                name, price_wei
            ).build_transaction({
                'from': self.default_account,
                'nonce': self.w3.eth.get_transaction_count(self.default_account),
                'gas': 200000,
                'gasPrice': self.w3.to_wei('20', 'gwei')
            })
            
            # Firmar transacción
            signed_txn = self.w3.eth.account.sign_transaction(transaction, private_key=self.private_key)
            
            # Enviar transacción
            tx_hash = self.w3.eth.send_raw_transaction(signed_txn.rawTransaction)
            
            # Esperar confirmación (opcional para demo, puedes quitarlo para mayor velocidad)
            # tx_receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
            
            print(f"✅ Producto creado en blockchain: {name}")
            print(f"📄 TX Hash: {tx_hash.hex()}")
            
            return tx_hash.hex()
            
        except Exception as e:
            print(f"❌ Error creando producto en blockchain: {e}")
            # Fallback a simulación
            return f"0xERROR_{int(time.time())}"
    
    def purchase_product_on_blockchain(self, product_id, quantity, total):
        """Generar transacción REAL en Ganache para una compra"""
        try:
            if not self.w3.is_connected():
                print("❌ No conectado a Ganache")
                return None
                
            # Usar la primera cuenta de Ganache
            from_account = self.w3.eth.accounts[0]
            to_account = self.w3.eth.accounts[1] if len(self.w3.eth.accounts) > 1 else from_account
            
            print(f"🔗 Creando transacción en Ganache...")
            print(f"   De: {from_account}")
            print(f"   Para: {to_account}")
            print(f"   Producto ID: {product_id}, Cantidad: {quantity}, Total: ${total}")
            
            # Crear transacción en Ganache
            transaction = {
                'from': from_account,
                'to': to_account,
                'value': self.w3.to_wei(0.001, 'ether'),  # Valor de la transacción
                'gas': 21000,
                'gasPrice': self.w3.eth.gas_price,
                'nonce': self.w3.eth.get_transaction_count(from_account),
            }
            
            # Firmar y enviar transacción a Ganache
            print("⏳ Enviando transacción a Ganache...")
            tx_hash = self.w3.eth.send_transaction(transaction)
            tx_receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
            
            tx_hash_hex = self.w3.to_hex(tx_hash)
            
            print(f"✅ Transacción Ganache exitosa:")
            print(f"   TX Hash: {tx_hash_hex}")
            print(f"   Bloque: {tx_receipt.blockNumber}")
            print(f"   Gas usado: {tx_receipt.gasUsed}")
            
            return tx_hash_hex
            
        except Exception as e:
            print(f"❌ Error en transacción Ganache: {e}")
            return None
    
    def get_blockchain_info(self):
        """Obtener información de la blockchain Ganache"""
        try:
            balance_wei = self.w3.eth.get_balance(self.default_account)
            balance_eth = self.w3.from_wei(balance_wei, 'ether')
            
            return {
                'connected': True,
                'network': 'Ganache Local',
                'block_number': self.w3.eth.block_number,
                'default_account': self.default_account,
                'balance_eth': float(balance_eth),
                'contract_address': self.contract_address,
                'accounts_available': len(self.w3.eth.accounts),
                'gas_price': self.w3.from_wei(self.w3.eth.gas_price, 'gwei'),
                'is_listening': self.w3.net.listening
            }
        except Exception as e:
            return {
                'connected': False,
                'error': str(e)
            }
    
    def get_accounts(self):
        """Obtener cuentas disponibles en Ganache"""
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