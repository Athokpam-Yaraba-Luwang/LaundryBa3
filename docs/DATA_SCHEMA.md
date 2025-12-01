# Data Schema

## Customers
- `phone` (PK): String
- `name`: String
- `address`: String
- `created_at`: Timestamp
- `profile_data`: JSON (preferences, etc.)

## Orders
- `order_id` (PK): String
- `customer_phone`: FK -> Customers.phone
- `status`: Enum (Pending, Finished, Delivered)
- `items`: List[JSON]
    - `item_id`: String
    - `type`: String
    - `color`: String
    - `fabric`: String
    - `care_instructions`: String
    - `price`: Float
    - `bbox`: [x, y, w, h]
- `total_price`: Float
- `created_at`: Timestamp
- `updated_at`: Timestamp
- `overlay_image_url`: String

## Fabric Knowledge Base
- `fabric_key` (PK): String (Hash of hints)
- `fabric_type`: String
- `care_instructions`: String
- `hints`: JSON

## Redeem Codes
- `code` (PK): String
- `customer_phone`: FK -> Customers.phone (Optional)
- `type`: Enum (FirstTime, Personal)
- `discount`: String
- `is_used`: Boolean
- `created_at`: Timestamp

## Feedback
- `feedback_id` (PK): String
- `order_id`: FK -> Orders.order_id
- `rating`: Integer (1-5)
- `comment`: String
- `created_at`: Timestamp
