// scripts/deploy.js
import pkg from 'hardhat';
const { ethers } = pkg;
import fs from "fs";

async function main() {
  console.log("🚀 Iniciando deployment del contrato ECommerce...");
  
  const [deployer] = await ethers.getSigners();
  console.log("📝 Desplegando con la cuenta:", deployer.address);
  
  const balance = await deployer.getBalance();
  console.log("💰 Balance de la cuenta:", ethers.utils.formatEther(balance), "ETH");

  // Desplegar el contrato
  const ECommerce = await ethers.getContractFactory("ECommerce");
  console.log("📦 Compilando contrato...");
  
  const ecommerce = await ECommerce.deploy();
  console.log("⏳ Esperando confirmación...");
  
  await ecommerce.deployed();
  
  console.log("✅ ECommerce contract deployed to:", ecommerce.address);
  
  // Guardar información del deployment
  const deploymentInfo = {
    contractAddress: ecommerce.address,
    deployer: deployer.address,
    network: "sepolia",
    timestamp: new Date().toISOString(),
    blockNumber: await ethers.provider.getBlockNumber()
  };
  
  fs.writeFileSync('deployment-info.json', JSON.stringify(deploymentInfo, null, 2));
  console.log("📁 Información de deployment guardada en: deployment-info.json");
  
  // Verificar el contrato (opcional)
  console.log("🎉 Deployment completado exitosamente!");
  console.log("🔗 Contrato:", ecommerce.address);
  console.log("👤 Desplegado por:", deployer.address);
}

main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error("❌ Error en el deployment:", error);
    process.exit(1);
  });