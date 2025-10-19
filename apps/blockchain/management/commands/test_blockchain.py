# management/commands/test_blockchain.py
from django.core.management.base import BaseCommand
from blockchain.alchemy_integration import BlockchainService

class Command(BaseCommand):
    help = 'Test blockchain integration'

    def handle(self, *args, **options):
        service = BlockchainService()
        
        # Test conexión
        connected, message = service.check_connection()
        self.stdout.write(f"🔗 {message}")
        
        if connected:
            # Test registrar producto
            result = service.register_product("Producto Test", 100000000000000000, 10)  # 0.1 ETH
            if result['success']:
                self.stdout.write(
                    self.style.SUCCESS(f"✅ Producto registrado: {result['tx_hash']}")
                )
            else:
                self.stdout.write(
                    self.style.ERROR(f"❌ Error: {result['error']}")
                )