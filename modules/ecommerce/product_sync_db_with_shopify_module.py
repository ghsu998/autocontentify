from modules.api.shopify_api import get_shopify_products
from modules.database.db_connection import connect_db
import logging

# Set up logging configuration
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def save_to_db(query, data):
    """Generic function to execute an insert/update query."""
    connection = connect_db()
    try:
        cursor = connection.cursor()
        cursor.execute(query, data)
        connection.commit()
        logging.info("Data saved successfully.")
        return cursor.lastrowid  # Return last inserted ID (used for foreign key reference)
    except Exception as e:
        logging.error(f"Error saving data to DB: {e}")
    finally:
        connection.close()

def save_product_to_db(product):
    """Save product and its variants to the database."""
    logging.info(f"Processing product: {product['title']}")

    product_data = (
        product['id'],
        product['title'],
        product.get('body_html', None),
        product['variants'][0].get('price', 0.0),
        product['variants'][0].get('inventory_quantity', 0),
        product.get('product_type', None),
        product.get('created_at', None),
        product.get('updated_at', None),
        product.get('vendor', None),
        product['variants'][0].get('weight', 0),
        ','.join([img['src'] for img in product.get('images', [])]) if product.get('images') else None,
        product['variants'][0].get('inventory_policy', 'deny'),
        product.get('status', 'active'),
        product['variants'][0].get('weight_unit', 'kg')
    )

    insert_query = """
        INSERT INTO products (
            shopify_product_id, name, description, price, stock, category_id, created_at, updated_at, 
            vendor, weight, images, inventory_policy, status, weight_unit, last_updated_at
        ) 
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP())
        ON DUPLICATE KEY UPDATE 
            name = VALUES(name), 
            description = VALUES(description), 
            price = VALUES(price), 
            stock = VALUES(stock), 
            category_id = VALUES(category_id), 
            updated_at = CURRENT_TIMESTAMP(),
            vendor = VALUES(vendor),
            weight = VALUES(weight),
            images = VALUES(images),
            inventory_policy = VALUES(inventory_policy),
            status = VALUES(status),
            weight_unit = VALUES(weight_unit),
            last_updated_at = CURRENT_TIMESTAMP();
    """

    # Insert product and get the product ID
    product_id = save_to_db(insert_query, product_data)

    # Save variants for the product using the correct product_id
    for variant in product['variants']:
        logging.info(f"Processing variant: {variant['title']} for product ID: {product_id}")
        save_variant_to_db(product_id, variant)

def save_variant_to_db(product_id, variant):
    """Save product variant data to the database."""
    variant_data = (
        product_id,  # Foreign key to products table
        variant['id'],
        variant['title'],
        variant['price'],
        variant['sku'],
        variant['inventory_quantity'],
        variant.get('weight', 0),
        variant.get('weight_unit', 'lb'),
    )

    insert_query = """
        INSERT INTO product_variants (
            product_id, variant_id, variant_title, price, sku, inventory_quantity, variant_weight, variant_weight_unit, created_at, last_updated_at
        ) 
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP())
        ON DUPLICATE KEY UPDATE 
            variant_title = VALUES(variant_title), 
            price = VALUES(price),
            sku = VALUES(sku),
            inventory_quantity = VALUES(inventory_quantity),
            variant_weight = VALUES(variant_weight),
            variant_weight_unit = VALUES(variant_weight_unit),
            last_updated_at = CURRENT_TIMESTAMP();
    """
    
    save_to_db(insert_query, variant_data)

def sync_products_with_shopify():
    """Main function to sync products from Shopify to the local database."""
    logging.info("Starting Shopify products sync...")
    
    products = get_shopify_products()  # Fetch products from Shopify
    if products:
        logging.info(f"Successfully fetched {len(products)} products.")
        for product in products:
            save_product_to_db(product)  # Save each product and its variants
    else:
        logging.error("No products found or API request failed.")

if __name__ == "__main__":
    sync_products_with_shopify()