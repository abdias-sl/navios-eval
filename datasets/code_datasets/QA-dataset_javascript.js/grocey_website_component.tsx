import React, { useState } from 'react';
import { ShoppingCart, Plus, Minus, Search, Star, Leaf, Clock, Truck } from 'lucide-react';

interface Product {
  id: number;
  name: string;
  category: string;
  price: number;
  image: string;
  rating: number;
  organic?: boolean;
  description: string;
}

interface CartItem extends Product {
  quantity: number;
}

interface Category {
  id: string;
  name: string;
  icon: string;
}

const GroceryWebsite: React.FC = () => {
  const [cart, setCart] = useState<CartItem[]>([]);
  const [searchTerm, setSearchTerm] = useState<string>('');
  const [selectedCategory, setSelectedCategory] = useState<string>('all');
  const [showCart, setShowCart] = useState<boolean>(false);

  const categories: Category[] = [
    { id: 'all', name: 'All Products', icon: '🛒' },
    { id: 'fruits', name: 'Fruits', icon: '🍎' },
    { id: 'vegetables', name: 'Vegetables', icon: '🥕' },
    { id: 'dairy', name: 'Dairy', icon: '🥛' },
    { id: 'meat', name: 'Meat & Fish', icon: '🥩' },
    { id: 'bakery', name: 'Bakery', icon: '🍞' },
    { id: 'pantry', name: 'Pantry', icon: '🥫' }
  ];

  const products: Product[] = [
    { id: 1, name: 'Organic Apples', category: 'fruits', price: 3.99, image: '🍎', rating: 4.5, organic: true, description: 'Fresh organic apples from local farms' },
    { id: 2, name: 'Fresh Bananas', category: 'fruits', price: 2.49, image: '🍌', rating: 4.2, description: 'Ripe yellow bananas perfect for snacking' },
    { id: 3, name: 'Orange Juice', category: 'fruits', price: 4.99, image: '🍊', rating: 4.7, description: 'Freshly squeezed orange juice' },
    { id: 4, name: 'Carrots', category: 'vegetables', price: 1.99, image: '🥕', rating: 4.3, organic: true, description: 'Crisp organic carrots' },
    { id: 5, name: 'Broccoli', category: 'vegetables', price: 2.99, image: '🥦', rating: 4.1, description: 'Fresh green broccoli crowns' },
    { id: 6, name: 'Bell Peppers', category: 'vegetables', price: 3.49, image: '🫑', rating: 4.4, description: 'Colorful bell peppers' },
    { id: 7, name: 'Whole Milk', category: 'dairy', price: 3.29, image: '🥛', rating: 4.6, description: 'Fresh whole milk' },
    { 8, name: 'Cheddar Cheese', category: 'dairy', price: 5.99, image: '🧀', rating: 4.8, description: 'Aged cheddar cheese' },
    { id: 9, name: 'Greek Yogurt', category: 'dairy', price: 4.49, image: '🥛', rating: 4.5, description: 'Creamy Greek yogurt' },
    { id: 10, name: 'Salmon Fillet', category: 'meat', price: 12.99, image: '🐟', rating: 4.7, description: 'Fresh Atlantic salmon' },
    { id: 11, name: 'Chicken Breast', category: 'meat', price: 8.99, image: '🍗', rating: 4.4, description: 'Boneless chicken breast' },
    { id: 12, name: 'Ground Beef', category: 'meat', price: 9.99, image: '🥩', rating: 4.3, description: 'Fresh ground beef' },
    { id: 13, name: 'Sourdough Bread', category: 'bakery', price: 4.99, image: '🍞', rating: 4.6, description: 'Artisan sourdough bread' },
    { id: 14, name: 'Croissants', category: 'bakery', price: 3.99, image: '🥐', rating: 4.2, description: 'Buttery French croissants' },
    { id: 15, name: 'Pasta', category: 'pantry', price: 2.49, image: '🍝', rating: 4.1, description: 'Premium pasta' },
    { id: 16, name: 'Rice', category: 'pantry', price: 3.99, image: '🍚', rating: 4.0, description: 'Long grain white rice' },
    { id: 17, name: 'Olive Oil', category: 'pantry', price: 7.99, image: '🫒', rating: 4.8, description: 'Extra virgin olive oil' },
    { id: 18, name: 'Tomatoes', category: 'vegetables', price: 2.99, image: '🍅', rating: 4.2, description: 'Fresh ripe tomatoes' },
    { id: 19, name: 'Strawberries', category: 'fruits', price: 4.99, image: '🍓', rating: 4.6, organic: true, description: 'Sweet organic strawberries' },
    { id: 20, name: 'Avocados', category: 'fruits', price: 5.99, image: '🥑', rating: 4.4, description: 'Ripe avocados' }
  ];

  const filteredProducts = products.filter(product => {
    const matchesSearch = product.name.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesCategory = selectedCategory === 'all' || product.category === selectedCategory;
    return matchesSearch && matchesCategory;
  });

  const addToCart = (product: Product): void => {
    setCart(prev => {
      const existing = prev.find(item => item.id === product.id);
      if (existing) {
        return prev.map(item =>
          item.id === product.id ? { ...item, quantity: item.quantity + 1 } : item
        );
      }
      return [...prev, { ...product, quantity: 1 }];
    });
  };

  const removeFromCart = (productId: number): void => {
    setCart(prev => {
      const existing = prev.find(item => item.id === productId);
      if (existing && existing.quantity > 1) {
        return prev.map(item =>
          item.id === productId ? { ...item, quantity: item.quantity - 1 } : item
        );
      }
      return prev.filter(item => item.id !== productId);
    });
  };

  const getCartTotal = (): number => {
    return cart.reduce((total, item) => total + (item.price * item.quantity), 0);
  };

  const getCartItemCount = (): number => {
    return cart.reduce((total, item) => total + item.quantity, 0);
  };

  const ProductCard: React.FC<{ product: Product }> = ({ product }) => (
    <div className="bg-white rounded-xl shadow-lg hover:shadow-xl transition-all duration-300 overflow-hidden border border-gray-100">
      <div className="relative">
        <div className="h-48 bg-gradient-to-br from-green-50 to-blue-50 flex items-center justify-center">
          <span className="text-6xl">{product.image}</span>
        </div>
        {product.organic && (
          <div className="absolute top-2 right-2 bg-green-500 text-white px-2 py-1 rounded-full text-xs flex items-center">
            <Leaf className="w-3 h-3 mr-1" />
            Organic
          </div>
        )}
      </div>
      
      <div className="p-4">
        <h3 className="font-bold text-lg mb-2 text-gray-800">{product.name}</h3>
        <p className="text-gray-600 text-sm mb-3">{product.description}</p>
        
        <div className="flex items-center mb-3">
          <div className="flex items-center">
            <Star className="w-4 h-4 text-yellow-400 fill-current" />
            <span className="ml-1 text-sm text-gray-600">{product.rating}</span>
          </div>
        </div>
        
        <div className="flex items-center justify-between">
          <span className="text-2xl font-bold text-green-600">${product.price}</span>
          <button
            onClick={() => addToCart(product)}
            className="bg-green-500 hover:bg-green-600 text-white px-4 py-2 rounded-lg flex items-center transition-colors duration-200"
          >
            <Plus className="w-4 h-4 mr-1" />
            Add
          </button>
        </div>
      </div>
    </div>
  );

  const CartItem: React.FC<{ item: CartItem }> = ({ item }) => (
    <div className="flex items-center justify-between py-3 border-b border-gray-200">
      <div className="flex items-center">
        <span className="text-2xl mr-3">{item.image}</span>
        <div>
          <h4 className="font-semibold text-gray-800">{item.name}</h4>
          <p className="text-sm text-gray-600">${item.price} each</p>
        </div>
      </div>
      
      <div className="flex items-center">
        <button
          onClick={() => removeFromCart(item.id)}
          className="bg-red-100 hover:bg-red-200 text-red-600 w-8 h-8 rounded-full flex items-center justify-center transition-colors duration-200"
        >
          <Minus className="w-4 h-4" />
        </button>
        <span className="mx-3 font-semibold">{item.quantity}</span>
        <button
          onClick={() => addToCart(item)}
          className="bg-green-100 hover:bg-green-200 text-green-600 w-8 h-8 rounded-full flex items-center justify-center transition-colors duration-2"
        >
          <Plus className="w-4 h-4" />
        </button>
      </div>
    </div>
  );

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-lg sticky top-0 z-50">
        <div className="container mx-auto px-4">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center">
              <div className="text-2xl font-bold text-green-600 mr-8">🛒 FreshMart</div>
              <nav className="hidden md:flex space-x-6">
                <a href="#" className="text-gray-700 hover:text-green-600 transition-colors">Home</a>
                <a href="#" className="text-gray-700 hover:text-green-600 transition-colors">About</a>
                <a href="#" className="text-gray-700 hover:text-green-600 transition-colors">Contact</a>
              </nav>
            </div>
            
            <div className="flex items-center space-x-4">
              <div className="relative">
                <Search className="w-5 h-5 absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" />
                <input
                  type="text"
                  placeholder="Search products..."
                  className="pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-transparent"
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                />
              </div>
              
              <button
                onClick={() => setShowCart(!showCart)}
                className="relative bg-green-500 hover:bg-green-600 text-white p-2 rounded-lg transition-colors duration-200"
              >
                <ShoppingCart className="w-6 h-6" />
                {getCartItemCount() > 0 && (
                  <span className="absolute -top-2 -right-2 bg-red-500 text-white text-xs rounded-full w-5 h-5 flex items-center justify-center">
                    {getCartItemCount()}
                  </span>
                )}
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <section className="bg-gradient-to-r from-green-600 to-blue-600 text-white py-16">
        <div className="container mx-auto px-4 text-center">
          <h1 className="text-5xl font-bold mb-6">Fresh Groceries Delivered</h1>
          <p className="text-xl mb-8">Farm-fresh produce and quality groceries at your doorstep</p>
          <div className="flex justify-center space-x-8">
            <div className="flex items-center">
              <Clock className="w-6 h-6 mr-2" />
              <span>Same-day delivery</span>
            </div>
            <div className="flex items-center">
              <Truck className="w-6 h-6 mr-2" />
              <span>Free shipping over $50</span>
            </div>
            <div className="flex items-center">
              <Leaf className="w-6 h-6 mr-2" />
              <span>Organic options</span>
            </div>
          </div>
        </div>
      </section>

      <div className="container mx-auto px-4 py-8">
        <div className="flex flex-col lg:flex-row gap-8">
          {/* Categories Sidebar */}
          <div className="lg:w-64">
            <div className="bg-white rounded-xl shadow-lg p-6 sticky top-24">
              <h2 className="text-xl font-bold mb-4 text-gray-800">Categories</h2>
              <div className="space-y-2">
                {categories.map(category => (
                  <button
                    key={category.id}
                    onClick={() => setSelectedCategory(category.id)}
                    className={`w-full text-left px-4 py-3 rounded-lg flex items-center transition-colors duration-200 ${
                      selectedCategory === category.id
                        ? 'bg-green-100 text-green-600 border-2 border-green-200'
                        : 'hover:bg-gray-100 text-gray-700'
                    }`}
                  >
                    <span className="mr-3 text-lg">{category.icon}</span>
                    {category.name}
                  </button>
                ))}
              </div>
            </div>
          </div>

          {/* Products Grid */}
          <div className="flex-1">
            <div className="flex justify-between items-center mb-6">
              <h2 className="text-2xl font-bold text-gray-800">
                {selectedCategory === 'all' ? 'All Products' : categories.find(c => c.id === selectedCategory)?.name}
              </h2>
              <span className="text-gray-600">{filteredProducts.length} products</span>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {filteredProducts.map(product => (
                <ProductCard key={product.id} product={product} />
              ))}
            </div>
            
            {filteredProducts.length === 0 && (
              <div className="text-center py-12">
                <div className="text-6xl mb-4">🔍</div>
                <h3 className="text-xl font-semibold text-gray-700 mb-2">No products found</h3>
                <p className="text-gray-600">Try adjusting your search or browse different categories</p>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Shopping Cart Sidebar */}
      <div className={`fixed top-0 right-0 h-full w-96 bg-white shadow-2xl transform transition-transform duration-300 z-50 ${
        showCart ? 'translate-x-0' : 'translate-x-full'
      }`}>
        <div className="p-6 border-b border-gray-200">
          <div className="flex items-center justify-between">
            <h2 className="text-xl font-bold text-gray-800">Shopping Cart</h2>
            <button
              onClick={() => setShowCart(false)}
              className="text-gray-500 hover:text-gray-700 text-2xl"
            >
              ×
            </button>
          </div>
        </div>
        
        <div className="flex-1 overflow-y-auto p-6">
          {cart.length === 0 ? (
            <div className="text-center py-12">
              <div className="text-6xl mb-4">🛒</div>
              <h3 className="text-lg font-semibold text-gray-700 mb-2">Your cart is empty</h3>
              <p className="text-gray-600">Add some delicious items to get started!</p>
            </div>
          ) : (
            <div className="space-y-2">
              {cart.map(item => (
                <CartItem key={item.id} item={item} />
              ))}
            </div>
          )}
        </div>
        
        {cart.length > 0 && (
          <div className="p-6 border-t border-gray-200">
            <div className="flex justify-between items-center mb-4">
              <span className="text-lg font-semibized text-gray-800">Total:</span>
              <span className="text-2xl font-bold text-green-600">${getCartTotal().toFixed(2)}</span>
            </div>
            <button className="w-full bg-green-500 hover:bg-green-600 text-white py-3 rounded-lg font-semibold transition-colors duration-200">
              Checkout
            </button>
          </div>
        )}
      </div>

      {/* Overlay */}
      {showCart && (
        <div 
          className="fixed inset-0 bg-black bg-opacity-50 z-40"
          onClick={() => setShowCart(false)}
        />
      )}

      {/* Footer */}
      <footer className="bg-gray-800 text-white py-12 mt-16">
        <div className="container mx-auto px-4">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
            <div>
              <h3 className="text-xl font-bold mb-4">🛒 FreshMart</h3>
              <p className="text-gray-400">Your trusted partner for fresh, quality groceries delivered right to your door.</p>
            </div>
            <div>
              <h4 className="font-semibold mb-4">Quick Links</h4>
              <ul className="space-y-2 text-gray-400">
                <li><a href="#" className="hover:text-white transition-colors">About Us</a></li>
                <li><a href="#" className="hover:text-white transition-colors">Contact</a></li>
                <li><a href="#" className="hover:text-white transition-colors">FAQ</a></li>
              </ul>
            </div>
            <div>
              <h4 className="font-semibold mb-4">Categories</h4>
              <ul className="space-y-2 text-gray-400">
                <li><a href="#" className="hover:text-white transition-colors">Fresh Produce</a></li>
                <li><a href="#" className="hover:text-white transition-colors">Dairy & Eggs</a></li>
                <li><a href="#" className="hover:text-white transition-colors">Meat & Seafood</a></li>
              </ul>
            </div>
            <div>
              <h4 className="font-semibold mb-4">Customer Service</h4>
              <ul className="space-y-2 text-gray-400">
                <li>📞 1-800-FRESH-99</li>
                <li>📧 support@freshmarket.com</li>
                <li>🕒 Mon-Fri: 8AM-8PM</li>
              </ul>
            </div>
          </div>
          <div className="border-t border-gray-700 mt-8 pt-8 text-center text-gray-400">
            <p>&copy; 2025 FreshMart. All rights reserved.</p>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default GroceryWebsite;