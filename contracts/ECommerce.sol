// contracts/ECommerce.sol
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

contract ECommerce {
    struct Product {
        uint256 id;
        string name;
        uint256 price;
        uint256 stock;
        address creator;
        uint256 createdAt;
        bool exists;
    }
    
    struct Purchase {
        uint256 purchaseId;
        uint256 productId;
        address buyer;
        uint256 quantity;
        uint256 totalPrice;
        uint256 purchasedAt;
        string productData;
    }
    
    address public owner;
    uint256 public productCount;
    uint256 public purchaseCount;
    
    mapping(uint256 => Product) public products;
    mapping(uint256 => Purchase) public purchases;
    mapping(address => uint256[]) public userPurchases;
    
    event ProductRegistered(
        uint256 indexed productId,
        string name,
        uint256 price,
        uint256 stock,
        address creator
    );
    
    event ProductPurchased(
        uint256 indexed purchaseId,
        uint256 indexed productId,
        address buyer,
        uint256 quantity,
        uint256 totalPrice,
        string productData
    );
    
    event StockUpdated(
        uint256 indexed productId,
        uint256 newStock
    );
    
    modifier onlyOwner() {
        require(msg.sender == owner, "Only owner can perform this action");
        _;
    }
    
    constructor() {
        owner = msg.sender;
        productCount = 0;
        purchaseCount = 0;
    }
    
    function registerProduct(
        string memory _name,
        uint256 _price,
        uint256 _stock
    ) public onlyOwner returns (uint256) {
        require(bytes(_name).length > 0, "Product name cannot be empty");
        require(_price > 0, "Price must be greater than 0");
        
        productCount++;
        
        products[productCount] = Product({
            id: productCount,
            name: _name,
            price: _price,
            stock: _stock,
            creator: msg.sender,
            createdAt: block.timestamp,
            exists: true
        });
        
        emit ProductRegistered(
            productCount,
            _name,
            _price,
            _stock,
            msg.sender
        );
        
        return productCount;
    }
    
    function purchaseProduct(
        uint256 _productId,
        uint256 _quantity,
        string memory _productData
    ) public payable returns (uint256) {
        require(products[_productId].exists, "Product does not exist");
        require(_quantity > 0, "Quantity must be greater than 0");
        require(products[_productId].stock >= _quantity, "Insufficient stock");
        
        Product storage product = products[_productId];
        uint256 totalPrice = product.price * _quantity;
        require(msg.value >= totalPrice, "Insufficient ETH sent");
        
        // Update stock
        product.stock -= _quantity;
        
        purchaseCount++;
        
        purchases[purchaseCount] = Purchase({
            purchaseId: purchaseCount,
            productId: _productId,
            buyer: msg.sender,
            quantity: _quantity,
            totalPrice: totalPrice,
            purchasedAt: block.timestamp,
            productData: _productData
        });
        
        userPurchases[msg.sender].push(purchaseCount);
        
        // Refund excess ETH
        if (msg.value > totalPrice) {
            payable(msg.sender).transfer(msg.value - totalPrice);
        }
        
        emit ProductPurchased(
            purchaseCount,
            _productId,
            msg.sender,
            _quantity,
            totalPrice,
            _productData
        );
        
        emit StockUpdated(_productId, product.stock);
        
        return purchaseCount;
    }
    
    function updateStock(uint256 _productId, uint256 _newStock) public onlyOwner {
        require(products[_productId].exists, "Product does not exist");
        products[_productId].stock = _newStock;
        
        emit StockUpdated(_productId, _newStock);
    }
    
    function getProduct(uint256 _productId) public view returns (
        uint256 id,
        string memory name,
        uint256 price,
        uint256 stock,
        address creator,
        uint256 createdAt
    ) {
        require(products[_productId].exists, "Product does not exist");
        Product memory product = products[_productId];
        return (
            product.id,
            product.name,
            product.price,
            product.stock,
            product.creator,
            product.createdAt
        );
    }
    
    function getPurchase(uint256 _purchaseId) public view returns (
        uint256 purchaseId,
        uint256 productId,
        address buyer,
        uint256 quantity,
        uint256 totalPrice,
        uint256 purchasedAt,
        string memory productData
    ) {
        Purchase memory purchase = purchases[_purchaseId];
        return (
            purchase.purchaseId,
            purchase.productId,
            purchase.buyer,
            purchase.quantity,
            purchase.totalPrice,
            purchase.purchasedAt,
            purchase.productData
        );
    }
    
    function getUserPurchases(address _user) public view returns (uint256[] memory) {
        return userPurchases[_user];
    }
    
    function withdraw() public onlyOwner {
        uint256 balance = address(this).balance;
        require(balance > 0, "No funds to withdraw");
        payable(owner).transfer(balance);
    }
    
    function getContractBalance() public view returns (uint256) {
        return address(this).balance;
    }
}