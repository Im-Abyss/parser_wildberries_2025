from parser import WbParser

def main():
    parser = WbParser(headless=True)

    try:
        print("Поиск товаров...")
        products = parser.search_products("футболки мужские", max_pages=2)
        print(f"Найдено товаров: {len(products)}")
        
        detailed_products = []
        for i, product in enumerate(products[:3]):
            print(f"Парсинг товара {i+1}: {product['name']}")
            detailed_info = parser.parse_product_detail(product['url'])
            
            if detailed_info:
                detailed_products.append(detailed_info)
                
                if detailed_info['images']:
                    print("Скачивание изображений...")
                    downloaded = parser.download_images(
                        detailed_info['images'], 
                        detailed_info['name']
                    )
                    detailed_info['downloaded_images'] = downloaded

        parser.safe_to_json(detailed_products, 'wb_detailed_products.json')
        parser.safe_to_json(products, 'wb_all_products.json')

    except Exception as e:
        print(f"Ошибка:\n{str(e)}")
    finally:
        parser.close()

if __name__ == "__main__":
    main()