from .models import User, AuctionListing, Bid, Comment, Watchlist

def get_winner(listing_id):
    bids = Bid.objects.filter(auction_id=int(listing_id))
    
    d = {}
    try:
        for bid in bids:
            d[bid.bidder_user_id] = bid.amount
        max_bidder =  max(d, key=d.get)
    except ValueError:
        max_bidder = None
    return max_bidder

def get_listing_info(listing):
    bids = Bid.objects.filter(auction_id=int(listing.id))
        
    bid_amounts = []
    try:
        for bid in bids:
            bid_amounts.append(bid.amount)
        max_bid = max(bid_amounts)
    except ValueError:
        max_bid = None
        starting_bid = listing.starting_bid
    
    d = {
        "id": listing.id,
        "title": listing.title,
        "description": listing.description,
        "image_url": listing.image_url,
        "active": listing.active,
        "seller": listing.seller_user_id,
        "category": listing.category
    }
    
    if max_bid:
        d["bid"] = max_bid
    else:
        d["starting_bid"] = starting_bid

    if listing.active == False:
        d["winner"] = get_winner(listing.id)

    return d

