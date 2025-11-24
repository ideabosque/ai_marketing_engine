# ai_marketing_engine

## Model Architecture and Relationships

This module implements a comprehensive AI marketing engine with a well-structured data model built on DynamoDB. The models follow a nested resolver pattern for lazy loading of related entities through GraphQL.

### Core Models

#### 1. CorporationProfile
**Purpose**: Represents business entities (companies, franchises, organizations)

**Table**: `ame-corporation_profiles`

**Key Attributes**:
- `corporation_uuid` (Range Key): Unique identifier
- `external_id`: External system identifier
- `corporation_type`: Type of corporation
- `business_name`: Corporation name
- `categories`: Business categories (List)
- `address`: Physical address
- `data`: Dynamic attributes stored via AttributeValue model

**Indexes**:
- `external_id-index`: Query by external ID
- `corporation_type-index`: Query by corporation type

#### 2. Place
**Purpose**: Physical locations associated with corporations

**Table**: `ame-places`

**Key Attributes**:
- `place_uuid` (Range Key): Unique identifier
- `region`: Geographic region
- `latitude`, `longitude`: Geo-coordinates
- `business_name`: Location name
- `address`: Physical address
- `types`: Place types (List)
- `corporation_uuid`: Reference to parent corporation (nullable)

**Relationships**:
- **Many-to-One** with CorporationProfile: `Place.corporation_uuid → CorporationProfile.corporation_uuid`

**Indexes**:
- `region-index`: Query places by region

**Nested Resolvers**:
- `corporation_profile`: Lazy loads the associated corporation (via [place.py:37](ai_marketing_engine/types/place.py#L37))

#### 3. ContactProfile
**Purpose**: Individual contact/customer profiles

**Table**: `ame-contact_profiles`

**Key Attributes**:
- `contact_uuid` (Range Key): Unique identifier
- `email`: Contact email (unique per endpoint)
- `first_name`, `last_name`: Contact name
- `place_uuid`: Reference to associated place
- `data`: Dynamic attributes stored via AttributeValue model

**Relationships**:
- **Many-to-One** with Place: `ContactProfile.place_uuid → Place.place_uuid`

**Indexes**:
- `email-index`: Query by email (with uniqueness validation at [contact_profile.py:203](ai_marketing_engine/models/contact_profile.py#L203-L213))
- `place_uuid-index`: Query contacts by place

**Nested Resolvers**:
- `place`: Lazy loads the associated place (via [contact_profile.py:36](ai_marketing_engine/types/contact_profile.py#L36))
- `data`: Lazy loads dynamic contact attributes (via [contact_profile.py:53](ai_marketing_engine/types/contact_profile.py#L53))

#### 4. ContactRequest
**Purpose**: Requests or inquiries from contacts

**Table**: `ame-contact_requests`

**Key Attributes**:
- `request_uuid` (Range Key): Unique identifier
- `contact_uuid`: Reference to contact
- `place_uuid`: Reference to place
- `request_title`: Request title
- `request_detail`: Detailed description

**Relationships**:
- **Many-to-One** with ContactProfile: `ContactRequest.contact_uuid → ContactProfile.contact_uuid`
- **Many-to-One** with Place: `ContactRequest.place_uuid → Place.place_uuid`

**Validation**: Contact profile must exist before creating request (enforced at [contact_request.py:189](ai_marketing_engine/models/contact_request.py#L189-L194))

**Indexes**:
- `place_uuid-index`: Query requests by place
- `contact_uuid-index`: Query requests by contact

**Nested Resolvers**:
- `contact_profile`: Lazy loads the associated contact (via [contact_request.py:32](ai_marketing_engine/types/contact_request.py#L32))

#### 5. AttributeValue
**Purpose**: Flexible key-value storage for dynamic attributes on contacts and corporations

**Table**: `ame-attribute_values`

**Key Attributes**:
- `data_type_attribute_name` (Hash Key): Format `{type}-{attribute_name}` (e.g., "contact-industry")
- `value_version_uuid` (Range Key): Version identifier
- `data_identity`: The UUID of the entity (contact_uuid or corporation_uuid)
- `value`: Attribute value
- `status`: `active` or `inactive` (versioning support)

**Relationships**:
- **One-to-Many** with ContactProfile: Multiple attributes per contact
- **One-to-Many** with CorporationProfile: Multiple attributes per corporation

**Versioning**: Only one active value per attribute; updating creates new version and inactivates previous (at [attribute_value.py:283](ai_marketing_engine/models/attribute_value.py#L283-L285))

**Indexes**:
- `data_identity-index`: Query by entity ID
- `data_identity-data_type_attribute_name-index`: Global index for efficient querying

**Usage**: Accessed via helper functions:
- `_insert_update_attribute_values()`: Save attributes (at [utils.py:115](ai_marketing_engine/models/utils.py#L115))
- `_get_data()`: Retrieve active attributes (at [utils.py:154](ai_marketing_engine/models/utils.py#L154))

#### 6. ActivityHistory
**Purpose**: Audit trail for entity changes

**Table**: `ame-activity_history`

**Key Attributes**:
- `id` (Hash Key): Entity identifier
- `timestamp` (Range Key): Unix timestamp
- `type`: Activity type
- `log`: Activity description
- `data_diff`: Changed data (MapAttribute)
- `updated_by`: User who made the change

**Relationships**:
- Generic tracking for any entity type (polymorphic via `type` and `id`)

**Indexes**:
- `type-id-index`: Global index for querying by entity type

### Relationship Diagram

```
CorporationProfile (1) ←──── (N) Place
                                 ↑
                                 │ (N)
                           ContactProfile (1) ←──── (N) ContactRequest
                                 ↑
                                 │ (N)
                                Place

ContactProfile (1) ←──── (N) AttributeValue (data_type="contact")
CorporationProfile (1) ←──── (N) AttributeValue (data_type="corporation")

ActivityHistory ← ← ← Any Entity (polymorphic tracking)
```

### Common Access Patterns

All models share a common key structure:
- **Hash Key**: `endpoint_id` (tenant isolation)
- **Range Key**: Entity-specific UUID

### Design Patterns

1. **Lazy Loading**: Nested entities are resolved on-demand via GraphQL field resolvers
2. **Versioning**: AttributeValue maintains history with active/inactive status
3. **Multi-tenancy**: All models partition by `endpoint_id`
4. **Flexible Schema**: Dynamic attributes stored in AttributeValue for extensibility
5. **Data Validation**: Cross-entity constraints (e.g., contact must exist before creating request)
6. **Audit Trail**: ActivityHistory provides comprehensive change tracking

### Helper Functions (utils.py)

- `_get_place()`: Fetches place with nested corporation_profile
- `_get_corporation_profile()`: Fetches corporation data
- `_get_contact_profile()`: Fetches contact with nested place
- `_insert_update_attribute_values()`: Manages versioned dynamic attributes
- `_get_data()`: Retrieves active attributes for an entity