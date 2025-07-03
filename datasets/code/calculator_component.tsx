import React, { useState, useEffect, useCallback } from 'react';

const Calculator = () => {
  const [display, setDisplay] = useState('0');
  const [previousValue, setPreviousValue] = useState(null);
  const [operation, setOperation] = useState(null);
  const [waitingForNewValue, setWaitingForNewValue] = useState(false);
  const [history, setHistory] = useState([]);
  const [memory, setMemory] = useState(0);
  const [isScientific, setIsScientific] = useState(false);
  const [isDegrees, setIsDegrees] = useState(true);

  // Handle keyboard input
  const handleKeyPress = useCallback((event) => {
    const { key } = event;
    
    if (key >= '0' && key <= '9') {
      inputNumber(key);
    } else if (key === '.') {
      inputDecimal();
    } else if (key === '+' || key === '-' || key === '*' || key === '/') {
      performOperation(key);
    } else if (key === 'Enter' || key === '=') {
      calculate();
    } else if (key === 'Escape' || key === 'c' || key === 'C') {
      clearAll();
    } else if (key === 'Backspace') {
      backspace();
    }
  }, [display, previousValue, operation, waitingForNewValue]);

  useEffect(() => {
    document.addEventListener('keydown', handleKeyPress);
    return () => document.removeEventListener('keydown', handleKeyPress);
  }, [handleKeyPress]);

  const inputNumber = (num) => {
    if (waitingForNewValue) {
      setDisplay(String(num));
      setWaitingForNewValue(false);
    } else {
      setDisplay(display === '0' ? String(num) : display + num);
    }
  };

  const inputDecimal = () => {
    if (waitingForNewValue) {
      setDisplay('0.');
      setWaitingForNewValue(false);
    } else if (display.indexOf('.') === -1) {
      setDisplay(display + '.');
    }
  };

  const clearAll = () => {
    setDisplay('0');
    setPreviousValue(null);
    setOperation(null);
    setWaitingForNewValue(false);
  };

  const clearEntry = () => {
    setDisplay('0');
  };

  const backspace = () => {
    if (display.length > 1) {
      setDisplay(display.slice(0, -1));
    } else {
      setDisplay('0');
    }
  };

  const performOperation = (nextOperation) => {
    const inputValue = parseFloat(display);

    if (previousValue === null) {
      setPreviousValue(inputValue);
    } else if (operation) {
      const currentValue = previousValue || 0;
      const newValue = calculate(currentValue, inputValue, operation);

      setDisplay(String(newValue));
      setPreviousValue(newValue);
      
      // Add to history
      setHistory(prev => [...prev, `${currentValue} ${operation} ${inputValue} = ${newValue}`]);
    }

    setWaitingForNewValue(true);
    setOperation(nextOperation);
  };

  const calculate = (firstValue, secondValue, operation) => {
    switch (operation) {
      case '+':
        return firstValue + secondValue;
      case '-':
        return firstValue - secondValue;
      case '*':
        return firstValue * secondValue;
      case '/':
        return secondValue !== 0 ? firstValue / secondValue : 0;
      case '^':
        return Math.pow(firstValue, secondValue);
      case 'mod':
        return firstValue % secondValue;
      default:
        return secondValue;
    }
  };

  const performCalculation = () => {
    const inputValue = parseFloat(display);

    if (previousValue !== null && operation) {
      const newValue = calculate(previousValue, inputValue, operation);
      
      setDisplay(String(newValue));
      setHistory(prev => [...prev, `${previousValue} ${operation} ${inputValue} = ${newValue}`]);
      setPreviousValue(null);
      setOperation(null);
      setWaitingForNewValue(true);
    }
  };

  // Scientific functions
  const performScientificOperation = (func) => {
    const value = parseFloat(display);
    let result;

    switch (func) {
      case 'sin':
        result = Math.sin(isDegrees ? value * Math.PI / 180 : value);
        break;
      case 'cos':
        result = Math.cos(isDegrees ? value * Math.PI / 180 : value);
        break;
      case 'tan':
        result = Math.tan(isDegrees ? value * Math.PI / 180 : value);
        break;
      case 'log':
        result = Math.log10(value);
        break;
      case 'ln':
        result = Math.log(value);
        break;
      case 'sqrt':
        result = Math.sqrt(value);
        break;
      case 'square':
        result = value * value;
        break;
      case 'factorial':
        result = factorial(Math.floor(value));
        break;
      case 'inverse':
        result = 1 / value;
        break;
      case 'pi':
        result = Math.PI;
        break;
      case 'e':
        result = Math.E;
        break;
      default:
        result = value;
    }

    setDisplay(String(result));
    setHistory(prev => [...prev, `${func}(${value}) = ${result}`]);
    setWaitingForNewValue(true);
  };

  const factorial = (n) => {
    if (n < 0) return NaN;
    if (n === 0 || n === 1) return 1;
    let result = 1;
    for (let i = 2; i <= n; i++) {
      result *= i;
    }
    return result;
  };

  // Memory functions
  const memoryStore = () => {
    setMemory(parseFloat(display));
  };

  const memoryRecall = () => {
    setDisplay(String(memory));
    setWaitingForNewValue(true);
  };

  const memoryClear = () => {
    setMemory(0);
  };

  const memoryAdd = () => {
    setMemory(memory + parseFloat(display));
  };

  const memorySubtract = () => {
    setMemory(memory - parseFloat(display));
  };

  const clearHistory = () => {
    setHistory([]);
  };

  const Button = ({ onClick, className = '', children, disabled = false }) => (
    <button
      onClick={onClick}
      disabled={disabled}
      className={`p-3 rounded-lg font-semibold transition-all duration-200 transform hover:scale-105 active:scale-95 ${className} ${
        disabled ? 'opacity-50 cursor-not-allowed' : 'hover:shadow-lg'
      }`}
    >
      {children}
    </button>
  );

  return (
    <div className="max-w-4xl mx-auto p-6 bg-gray-100 min-h-screen">
      <div className="bg-white rounded-xl shadow-2xl p-6">
        <h1 className="text-3xl font-bold text-center mb-6 text-gray-800">
          Advanced Calculator
        </h1>
        
        <div className="flex flex-col lg:flex-row gap-6">
          {/* Calculator Section */}
          <div className="lg:w-2/3">
            {/* Display */}
            <div className="bg-gray-900 text-white p-4 rounded-lg mb-4">
              <div className="text-right">
                {previousValue !== null && operation && (
                  <div className="text-sm text-gray-400">
                    {previousValue} {operation}
                  </div>
                )}
                <div className="text-3xl font-mono overflow-hidden">
                  {display}
                </div>
                {memory !== 0 && (
                  <div className="text-xs text-blue-400">M: {memory}</div>
                )}
              </div>
            </div>

            {/* Mode Toggle */}
            <div className="flex justify-center mb-4">
              <button
                onClick={() => setIsScientific(!isScientific)}
                className="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors"
              >
                {isScientific ? 'Basic' : 'Scientific'} Mode
              </button>
              {isScientific && (
                <button
                  onClick={() => setIsDegrees(!isDegrees)}
                  className="ml-2 px-4 py-2 bg-green-500 text-white rounded-lg hover:bg-green-600 transition-colors"
                >
                  {isDegrees ? 'DEG' : 'RAD'}
                </button>
              )}
            </div>

            {/* Button Grid */}
            <div className={`grid gap-2 ${isScientific ? 'grid-cols-6' : 'grid-cols-4'}`}>
              {/* Scientific Functions (only shown in scientific mode) */}
              {isScientific && (
                <>
                  <Button onClick={() => performScientificOperation('sin')} className="bg-purple-500 text-white hover:bg-purple-600">
                    sin
                  </Button>
                  <Button onClick={() => performScientificOperation('cos')} className="bg-purple-500 text-white hover:bg-purple-600">
                    cos
                  </Button>
                  <Button onClick={() => performScientificOperation('tan')} className="bg-purple-500 text-white hover:bg-purple-600">
                    tan
                  </Button>
                  <Button onClick={() => performScientificOperation('log')} className="bg-purple-500 text-white hover:bg-purple-600">
                    log
                  </Button>
                  <Button onClick={() => performScientificOperation('ln')} className="bg-purple-500 text-white hover:bg-purple-600">
                    ln
                  </Button>
                  <Button onClick={() => performScientificOperation('factorial')} className="bg-purple-500 text-white hover:bg-purple-600">
                    n!
                  </Button>
                  
                  <Button onClick={() => performScientificOperation('sqrt')} className="bg-indigo-500 text-white hover:bg-indigo-600">
                    √
                  </Button>
                  <Button onClick={() => performScientificOperation('square')} className="bg-indigo-500 text-white hover:bg-indigo-600">
                    x²
                  </Button>
                  <Button onClick={() => performOperation('^')} className="bg-indigo-500 text-white hover:bg-indigo-600">
                    x^y
                  </Button>
                  <Button onClick={() => performScientificOperation('inverse')} className="bg-indigo-500 text-white hover:bg-indigo-600">
                    1/x
                  </Button>
                  <Button onClick={() => performScientificOperation('pi')} className="bg-indigo-500 text-white hover:bg-indigo-600">
                    π
                  </Button>
                  <Button onClick={() => performScientificOperation('e')} className="bg-indigo-500 text-white hover:bg-indigo-600">
                    e
                  </Button>
                </>
              )}

              {/* Memory Functions */}
              <Button onClick={memoryClear} className="bg-yellow-500 text-white hover:bg-yellow-600">
                MC
              </Button>
              <Button onClick={memoryRecall} className="bg-yellow-500 text-white hover:bg-yellow-600">
                MR
              </Button>
              <Button onClick={memoryStore} className="bg-yellow-500 text-white hover:bg-yellow-600">
                MS
              </Button>
              <Button onClick={memoryAdd} className="bg-yellow-500 text-white hover:bg-yellow-600">
                M+
              </Button>
              {isScientific && (
                <>
                  <Button onClick={memorySubtract} className="bg-yellow-500 text-white hover:bg-yellow-600">
                    M-
                  </Button>
                  <Button onClick={() => performOperation('mod')} className="bg-gray-500 text-white hover:bg-gray-600">
                    mod
                  </Button>
                </>
              )}

              {/* Clear Functions */}
              <Button onClick={clearAll} className="bg-red-500 text-white hover:bg-red-600">
                AC
              </Button>
              <Button onClick={clearEntry} className="bg-red-400 text-white hover:bg-red-500">
                CE
              </Button>
              <Button onClick={backspace} className="bg-red-400 text-white hover:bg-red-500">
                ⌫
              </Button>
              <Button onClick={() => performOperation('/')} className="bg-orange-500 text-white hover:bg-orange-600">
                ÷
              </Button>

              {/* Number and Operation Buttons */}
              <Button onClick={() => inputNumber('7')} className="bg-gray-200 hover:bg-gray-300">7</Button>
              <Button onClick={() => inputNumber('8')} className="bg-gray-200 hover:bg-gray-300">8</Button>
              <Button onClick={() => inputNumber('9')} className="bg-gray-200 hover:bg-gray-300">9</Button>
              <Button onClick={() => performOperation('*')} className="bg-orange-500 text-white hover:bg-orange-600">×</Button>

              <Button onClick={() => inputNumber('4')} className="bg-gray-200 hover:bg-gray-300">4</Button>
              <Button onClick={() => inputNumber('5')} className="bg-gray-200 hover:bg-gray-300">5</Button>
              <Button onClick={() => inputNumber('6')} className="bg-gray-200 hover:bg-gray-300">6</Button>
              <Button onClick={() => performOperation('-')} className="bg-orange-500 text-white hover:bg-orange-600">−</Button>

              <Button onClick={() => inputNumber('1')} className="bg-gray-200 hover:bg-gray-300">1</Button>
              <Button onClick={() => inputNumber('2')} className="bg-gray-200 hover:bg-gray-300">2</Button>
              <Button onClick={() => inputNumber('3')} className="bg-gray-200 hover:bg-gray-300">3</Button>
              <Button onClick={() => performOperation('+')} className="bg-orange-500 text-white hover:bg-orange-600">+</Button>

              <Button onClick={() => inputNumber('0')} className={`bg-gray-200 hover:bg-gray-300 ${!isScientific ? 'col-span-2' : ''}`}>0</Button>
              {isScientific && <Button className="bg-gray-200 opacity-50" disabled>.</Button>}
              <Button onClick={inputDecimal} className="bg-gray-200 hover:bg-gray-300">.</Button>
              <Button onClick={performCalculation} className="bg-blue-500 text-white hover:bg-blue-600">=</Button>
            </div>
          </div>

          {/* History Section */}
          <div className="lg:w-1/3">
            <div className="bg-gray-50 rounded-lg p-4 h-96 overflow-y-auto">
              <div className="flex justify-between items-center mb-4">
                <h3 className="text-lg font-semibold text-gray-700">History</h3>
                <button
                  onClick={clearHistory}
                  className="px-3 py-1 bg-red-500 text-white rounded hover:bg-red-600 text-sm"
                >
                  Clear
                </button>
              </div>
              {history.length === 0 ? (
                <p className="text-gray-500 text-center">No calculations yet</p>
              ) : (
                <div className="space-y-2">
                  {history.slice(-20).reverse().map((item, index) => (
                    <div
                      key={index}
                      className="text-sm font-mono bg-white p-2 rounded border cursor-pointer hover:bg-gray-100"
                      onClick={() => {
                        const result = item.split(' = ')[1];
                        setDisplay(result);
                        setWaitingForNewValue(true);
                      }}
                    >
                      {item}
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Calculator;