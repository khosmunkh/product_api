import re
import json
import threading
import requests
from lxml import html
import mysql.connector

host = 'localhost'
db_user = 'root'
db_password = ''
port = 3306
database = 'auction'
table_name = 'product_data'


class Auction:
    def __init__(self):
        self.headers = {
            'Accept': '*/*',
            'Accept-Language': 'en-GB,en-US;q=0.9,en;q=0.8',
            'Connection': 'keep-alive',
            'Referer': 'https://www.auction.co.kr/',
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36',
        }
        self.connection = self.create_connection()
        self.create_table()

    def create_connection(self):
        return mysql.connector.connect(
            host=host,
            user=db_user,
            password=db_password,
            port=port,
            database=database
        )

    def create_table(self):
        cursor = self.connection.cursor()

        try:
            cursor.execute(f"""
            CREATE TABLE IF NOT EXISTS {table_name} (
                id INT AUTO_INCREMENT PRIMARY KEY,
                categories_id TEXT,
                categories TEXT,
                image TEXT,
                Price FLOAT,
                discounted_price FLOAT,
                item_number TEXT,
                color TEXT
            )
            """)
            self.connection.commit()
            print(f"Table {table_name} created successfully.")
        except Exception as e:
            print(e)
        finally:
            cursor.close()

    def auction_url(self):
        response0 = requests.get(
            'https://script.auction.co.kr/common/HeaderCategoryInfo.js?1682504584411',
            headers=self.headers
        )
        while response0.status_code != 200:
            print(response0.status_code)
            response0 = requests.get(
                'https://script.auction.co.kr/common/HeaderCategoryInfo.js',
                headers=self.headers
            )
            break
        if response0.status_code == 200:
            category = response0.text.split("childCategoryHash['")
            for cat in category[1:]:
                category_id = re.findall("new HeaderCategoryT(.*?'),", cat)
                if category_id:
                    for cat_id in category_id:
                        cat_id = str(cat_id).replace("('", '').replace("'", '')
                        self.get_cat_link(cat_id)
                else:
                    continue
        else:
            """If Didn't get the proper response, call the same function to retry"""
            self.auction_url()

    def get_cat_link(self, cat_id):
        next_page = True
        page = 1
        while next_page:
            print('Page:', page)
            url = f'https://browse.auction.co.kr/list?category={cat_id}&p={page}'
            response = requests.get(url, headers=self.headers)
            dom = html.fromstring(response.text)
            try:
                all_products = dom.xpath('//a[@class="link--itemcard"]/@href')
            except:
                all_products = None

            if all_products is None:
                print('No Next Page')
                break
            else:
                threads = []
                cid = 1
                for product in all_products:
                    """Code for Multithread"""
                    threads.append(threading.Thread(target=self.product_details, args=(product, cid)))
                    threads[-1].start()
                    cid += 1

                for t in threads:
                    t.join()
                page += 1

    def product_details(self, product, cid):
        response_redirect = requests.get(product, headers=self.headers)
        try:
            product_url = response_redirect.text.split("replace('")[1].split("'")[0]
            print('Product Url:', product_url)
        except:
            try:
                product_url = product
                print('Product Url:', product_url)
            except:
                product_url = ''
                print('Product Url:', product_url)
                return

        response1 = requests.get(product_url, headers=self.headers)
        dom1 = html.fromstring(response1.text)
        try:
            category = []
            category_list = dom1.xpath('//div[@class="category_wrap"]/a//text()[1]')
            for cat in category_list:
                if '더보기' in cat:
                    continue
                else:
                    cat = cat.strip()
                    if cat:
                        category.append(cat)
        except:
            category = ''

        try:
            colors = []
            try:
                all_colors = dom1.xpath(
                    '//*[contains(text(),"색상")]/following::div[@class="item_block"][1]/ul/li/a'
                )
                if all_colors:
                    for all_col in all_colors:
                        color = all_col.xpath('.//text()')[0].strip()
                        if color in colors:
                            continue
                        else:
                            colors.append(color)
            except:
                colors = ''
        except:
            colors = ''

        try:
            j_data = response1.text.split("GroupItemList = $.parseJSON('[")[1].split("},")[0] + '}'
        except:
            j_data = ''

        if j_data:
            data = json.loads(j_data)
            try:
                discounted_price = ''.join(data['DiscountPrice']).replace(',', '')
            except:
                discounted_price = None
            try:
                original_price = ''.join(data['Price']).replace(',', '')
            except:
                original_price = None
            try:
                item_number = data['ItemNo']
            except:
                item_number = None
            try:
                product_image = data['GalleryImageUrl']
            except:
                product_image = None
        else:
            try:
                discounted_price = response1.text.split("var discountedPrice = '")[1].split("'")[0]
            except:
                discounted_price = ''
            try:
                original_price = response1.text.split("var itemPrice = '")[1].split("'")[0]
            except:
                original_price = ''
            item_number = product_url.split('itemno=')[1]
            try:
                product_image = dom1.xpath('//*[@class="thumb-gallery"]//li[@class=" on"]/a/img/@src')[0]
                if 'http' not in product_image:
                    product_image = 'http:' + product_image
            except:
                product_image = ''

        data = {
            'categories_id': f'categories_id_{cid}',
            'categories': ' | '.join(category),
            'image': product_image,
            'Price': float(original_price) if original_price else None,
            'discounted_price': float(discounted_price) if discounted_price else None,
            'item_number': item_number,
            'color': ', '.join(colors)
        }
        print(data)
        self.insert_to_db(data)

    def insert_to_db(self, table_dict):
        cursor = self.connection.cursor()

        field_list = []
        value_list = []
        for field, value in table_dict.items():
            field_list.append(field.strip())
            value_list.append(str(value).replace("'", "’").strip())

        fields = ','.join(field_list)
        placeholders = ','.join(['%s'] * len(value_list))
        insert_db = f"INSERT INTO {table_name} ({fields}) VALUES ({placeholders})"

        try:
            cursor.execute(insert_db, tuple(value_list))
            self.connection.commit()
            print(f'Data Inserted into {table_name}')
        except Exception as e:
            print(e)
        finally:
            cursor.close()


# Scrape hiij ehleh
Auction().auction_url()
