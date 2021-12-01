"""
/marketplace/products/most-selled
/marketplace/products/categories

/marketplace/stock-keeping-units
/marketplace/manufacturers
/marketplace/price-offers
/marketplace/retailers
/marketplace/products
/marketplace/brands
/marketplace/search
/marketplace/stats


/marketplace/stock-keeping-units/{stock_keeping_unit_id}/price-offers
/marketplace/products/object_classes/{class_name}
/marketplace/brands/{brand_id}/products
/marketplace/{element}s/{product_id}/image_urls
/marketplace/{element_name}s/{element_id}/url

/marketplace/stock-keeping-units/{stock_keeping_unit_id}
/marketplace/object_classes/{class_name}
/marketplace/manufacturers/{manufacturer_id}
/marketplace/price-offers/{price_offer_id}
/marketplace/retailers/{retailer_id}
/marketplace/products/{product_id}
/marketplace/brands/{brand_id}
/marketplace/{element_name}s
"""

from dessia_api_client.clients import PlatformApiClient


class Marketplace:
    def __init__(self, client: PlatformApiClient):
        self.client = client

    def get_element(self, element_name, element_id):
        return self.client.get('/marketplace/{element_name}s/{element_id}',
                               path_subs={'element_name': element_name,
                                          'element_id': element_id})

    # strange, why is there both filter & additional params ??
    def request_get_elements(self, element_name, limit, offset,
                             filters=None, order=None):
        if filters is None:
            filters = []
        parameters = {'limit': limit, 'offset': offset}
        for f in filters:
            parameters.update(f.to_param())

        if order is not None:
            parameters['order'] = order

        return self.client.get('/marketplace/{element_name}s',
                               params=parameters,
                               path_subs={'element_name': element_name})

    def get_products(self, limit=100, offset=0, filters=None):
        if filters is None:
            filters = []
        return self.request_get_elements('product', limit, offset, filters)

    def get_retailers(self, limit=20, offset=0, filters=None):
        if filters is None:
            filters = []
        return self.request_get_elements('retailer', limit, offset, filters)

    def request_create_retailer(self, name, url, country):
        data = {'name': name, 'url': url, 'country': country}

        return self.client.post('/marketplace/retailers',
                                json=data)

    def get_skus(self, limit=20, offset=0, filters=None):
        if filters is None:
            filters = []
        return self.request_get_elements('stock-keeping-unit', limit,
                                         offset, filters)

    def request_update_sku_price_offers(self, sku_id, new_price_offers):
        return self.client.put('/marketplace/stock-keeping-units/{sku_id}/price-offers',
                               json=new_price_offers,
                               path_subs={'sku_id': sku_id})

    def request_create_sku(self, product_id, number_products, url,
                           retailer_id, image_urls=None):
        data = {'product_id': product_id, 'number_products': number_products,
                'url': url, 'retailer_id': retailer_id}
        if image_urls is not None:
            data['image_urls'] = image_urls

        return self.client.post('/marketplace/stock-keeping-units',
                                json=data)

    def add_image_url_to_sku(self, product_id, image_url):
        return self.client.post('/marketplace/stock-keeping-units/{product_id}/image_urls',
                                path_subs={'product_id': product_id},
                                json={'url': image_url})

    def get_price_offers(self, limit=20, offset=0, filters=None):
        if filters is None:
            filters = []
        return self.request_get_elements('price-offer', limit, offset, filters)

    def request_create_price_offer(self, sku_id, unit_price, currency, min_quantity, max_quantity=None):
        data = {'sku_id': sku_id,
                'min_quantity': min_quantity,
                'unit_price': unit_price,
                'currency': currency,
                'max_quantity': max_quantity
                }

        return self.client.post('/marketplace/price-offers',
                                json=data)

    def request_marketplace_stats(self):
        return self.client.get('/marketplace/stats')

    def get_manufacturers(self, limit=20, offset=0, filters=None):
        if filters is None:
            filters = []
        return self.request_get_elements('manufacturer', limit, offset, filters=filters)

    def request_create_manufacturer(self, name, url, country):
        return self.client.post('marketplace/manufacturers',
                                json={'name': name,
                                      'url': url,
                                      'country': country})

    def get_brands(self, limit=20, offset=0, filters=None):
        if filters is None:
            filters = []
        return self.request_get_elements('brand', limit, offset, filters)

    def request_create_brand(self, name, url, country, manufacturer_id):
        data = {'name': name, 'url': url, 'country': country,
                'manufacturer_id': manufacturer_id}
        return self.client.post('/marketplace/brands',
                                json=data)

    def create_product(self, name, url, brand_id, object_class, object_id,
                       image_urls=None, documentation_url=None):
        data = {'name': name, 'url': url, 'brand_id': brand_id,
                'object_class': object_class, 'object_id': object_id}

        if image_urls is not None:
            data['image_urls'] = image_urls
        else:
            data['image_urls'] = []

        if documentation_url is not None:
            data['documentation_url'] = documentation_url

        return self.client.post('marketplace/products',
                                json=data)

    def add_image_url_to_product(self, product_id, image_url):
        return self.client.post('/marketplace/products/{product_id}/image_urls',
                                path_subs={'product_id': product_id},
                                json={'url': image_url})

    def get_all_elements(self, element_name, filters=None, query_size=500):
        elements = []
        offset = 0
        query_empty = False
        while not query_empty:
            callable_ = getattr(self, 'get_{}s'.format(element_name))
            results = callable_(limit=query_size, offset=offset,
                                filters=filters)
            query_list = results['filtered_results']
            query_empty = len(query_list) == 0
            elements.extend(query_list)
            offset += query_size
        return elements

    def plot_product_price_offers(self, product_id):
        current_time = int(time.time())
        filters = [EqualityFilter('sku.product.id', product_id)]
        price_offers = self.get_all_elements('price_offer', filters)
        fig, (ax1, ax2) = plt.subplots(nrows=2, sharex=True)

        sku_ids = []
        sku_labels = {}
        for price_offer in price_offers:
            sku_id = price_offer['stock_keeping_unit']['id']
            if sku_id not in sku_ids:
                sku_ids.append(sku_id)

            if sku_id not in sku_labels:
                sku_labels[sku_id] = '{} SKU {}'.format(
                    self.get_element('stock-keeping-unit', sku_id).json()['retailer']['name'],
                    sku_id)

        cmap = get_cmap('jet')
        sku_colors = {sku_id: cmap(ii / (len(sku_ids))) for ii, sku_id in enumerate(sku_ids)}
        labelled_sku = []
        handles = []
        labels = []
        for price_offer in price_offers:
            sku_id = price_offer['stock_keeping_unit']['id']
            if price_offer['validity_end'] is None:
                validity_end = current_time
            else:
                validity_end = price_offer['validity_end']

            handle, = ax1.plot([price_offer['validity_start'], validity_end],
                               [price_offer['unit_price']] * 2,
                               color=sku_colors[sku_id],
                               marker='o')
            ax1.text(0.5 * (validity_end + price_offer['validity_start']),
                     price_offer['unit_price'],
                     '{}-{}'.format(price_offer['min_quantity'], price_offer['max_quantity'])
                     )
            if sku_id not in labelled_sku:
                handles.append(handle)
                labels.append(sku_labels[sku_id])
                labelled_sku.append(sku_id)
        ax1.legend(handles, labels)
        ax1.set_title('Price offers')

        ax1.grid(True)

        product = self.get_element('product', product_id).json()
        price_by_qty = {}
        disappeared_qty = set()
        for timestamp, price_breaks in product['prices_history']:
            seen_qty_t = set()
            for quantity, unit_price in price_breaks:
                seen_qty_t.add(quantity)
                if quantity in disappeared_qty:
                    disappeared_qty.remove(quantity)
                if quantity in price_by_qty:
                    price_by_qty[quantity][0].append(timestamp)
                    price_by_qty[quantity][1].append(unit_price)
                else:
                    price_by_qty[quantity] = [[timestamp], [unit_price]]

            for quantity in price_by_qty.keys():
                if quantity not in seen_qty_t:
                    disappeared_qty.add(quantity)

            for quantity in disappeared_qty:
                price_by_qty[quantity][0].append(timestamp)
                price_by_qty[quantity][1].append(None)

        for quantity, (x, y) in price_by_qty.items():
            if y[-1] is not None:
                x.append(current_time)
                y.append(y[-1])

        n_qty = len(price_by_qty)
        for iq, (quantity, (x, y)) in enumerate(price_by_qty.items()):
            color = cmap(iq / n_qty)
            ax2.step(x, y, where='post', label='For {}'.format(quantity),
                     color=color)
            ax2.plot(x, y, 'o', color=color)

        ax2.set_title('Global price history')

        ax2.legend()

        ax1.grid(True)
        ax2.grid(True)
