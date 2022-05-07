# @version ^0.3.3
# @dev Implementation of minting on ERC-721.
# @author Arjuna Sky Kok (@arjunaskykok)

# Notice: Withdrawing ETH method is not implemented. Do it yourself!

maxElements: uint256
price: uint256

# @dev Mapping from NFT ID to the address that owns it.
idToOwner: HashMap[uint256, address]

# @dev Mapping from owner address to count of his tokens.
ownerToNFTokenCount: HashMap[address, uint256]

counter: uint256 # minting tracker

# @dev Emits when ownership of any NFT changes by any mechanism. This event emits when NFTs are
#      created (`from` == 0) and destroyed (`to` == 0). Exception: during contract creation, any
#      number of NFTs may be created and assigned without emitting Transfer. At the time of any
#      transfer, the approved address for that NFT (if any) is reset to none.
# @param _from Sender of NFT (if address is zero address it indicates token creation).
# @param _to Receiver of NFT (if address is zero address it indicates token destruction).
# @param _tokenId The NFT that got transfered.
event Transfer:
    _from: indexed(address)
    _to: indexed(address)
    _tokenId:indexed(uint256)


# Interface for the contract called by safeTransferFrom()
interface NFTReceiver:
    def onERC721Received(
            _operator: address,
            _from: address,
            _tokenId: uint256,
            _data: Bytes[1024]
        ) -> bytes32: view


# @dev Constructor
# @param _maxElements Maximum number of NFTs that can be minted
# @param _price Price of each NFT
@external
def __init__(_maxElements: uint256, _price: uint256):
    self.maxElements = _maxElements
    self.price = _price


# @dev Transfer NFT ownership
# @param _to The new owner of the NFT
# @param _tokenId The NFT to transfer
@internal
def _mint(_to: address, _tokenId: uint256):
    assert _to != ZERO_ADDRESS, "To is zero"
    assert self.idToOwner[_tokenId] == ZERO_ADDRESS, "Token already exists"

    self.ownerToNFTokenCount[_to] += 1
    self.idToOwner[_tokenId] = _to

    log Transfer(ZERO_ADDRESS, _to, _tokenId)


# @dev Mint a new NFT safely
# @param _to The address that will own the new NFT
# @param _id The token id of the NFT
@internal
def _safeMint(_to: address, _id: uint256):
    self._mint(_to, _id)
    _operator: address = ZERO_ADDRESS
    _data: Bytes[1024] = b""
    _from: address = self
    if(_to.codesize > 0):
        returnValue: bytes32 = NFTReceiver(_to).onERC721Received(_operator, _from, _id, _data)
        assert returnValue == method_id("onERC721Received(address,address,uint256,bytes)", output_type=bytes32)


# @dev Mint a new NFT
# @param _to The address that will own the new NFT
@internal
def _mintAnElement(_to: address):
    id: uint256 = self.counter
    self.counter += 1
    self._safeMint(_to, id)


# @dev Mint new NFTs
# @param _to The address that will own the new NFTs
# @param _count The number of NFTs to mint
@external
@payable
def mint(_to: address):
    total: uint256 = self.counter
    assert total < self.maxElements, "Sale end"
    assert msg.value >= self.price, "Not enough ETH"

    self._mintAnElement(_to)

    
# @dev Returns the number of NFTs owned by `_owner`. NFTs assigned to the zero address are
#      considered invalid, and this function throws for queries about the zero address.
# @param _owner Address for whom to query the balance.
@external
@view
def balanceOf(_owner: address) -> uint256:
    assert _owner != ZERO_ADDRESS
    return self.ownerToNFTokenCount[_owner]


# @dev Returns the address of the owner of the NFT. NFTs assigned to zero address are considered
#      invalid, and queries about them do throw.
# @param _tokenId The identifier for an NFT.
@external
@view
def ownerOf(_tokenId: uint256) -> address:
    assert self.idToOwner[_tokenId] != ZERO_ADDRESS
    return self.idToOwner[_tokenId]