from .models import Order,OrderItem

def no_of_orderitms(request):
    numbers = 0
    try:
        order = Order.objects.filter(user=request.user,isordered=False,from_buynow=False).first()
        if order:
            orderitems = OrderItem.objects.filter(order_id=order,isordered=False)
            numbers = orderitems.count()
        return {"numbers":numbers}
    except:
        return {"numbers":numbers}
    
def no_of_orders(request):
    order_count = 0
    try:
        order = Order.objects.filter(user=request.user,isordered=True)
        if order:
            order_count = order.count()
        return {"order_count":order_count}
    except:
        return {"order_count":order_count}