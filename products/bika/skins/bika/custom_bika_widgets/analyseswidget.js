function selectService(control_id, total_id) {
    
    total = getElem("id", total_id, null);
    tot_price = parseFloat(total.value);
    service = getElem("id", control_id, null);
    price = parseFloat(service.getAttribute('price'));
    if (service.checked) {
        tot_price = tot_price + price;
    }
    else {
        tot_price = tot_price - price;
    }

    total.value = tot_price.toFixed(2);

    return
}
