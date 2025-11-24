# Nested Resolver Development Plan

## Executive Summary

This document outlines the migration plan to convert the AI Marketing Engine from the current **eager-loading** approach (where nested data is embedded in JSON fields) to **lazy-loading with nested field resolvers** (where nested data is resolved on-demand via GraphQL field resolvers).

### Current State
- Nested data (place, corporation_profile, contact_profile, data) is embedded as JSON during type conversion
- `get_*_type` functions in models fetch and embed nested relationships
- GraphQL types use `JSON()` scalar for nested objects

### Target State
- Nested data is resolved lazily via GraphQL field resolvers
- `get_*_type` functions return minimal, flat data structures
- GraphQL types use strongly-typed `Field()` for nested relationships
- Better performance for queries that don't need nested data
- Consistent resolver pattern across all entity types

### Nested Relationship Chain
This migration covers a **4-level nesting chain**:
```
ContactRequest
  → ContactProfile
      → Place
          → CorporationProfile
```

---

## Migration Phases

### Phase 1: Preparation & Infrastructure (No Breaking Changes)
**Goal:** Set up foundation without affecting current functionality

#### 1.1 Create Migration Branch
```bash
git checkout -b feature/nested-resolvers
```

#### 1.2 Add Utility Functions (if missing)
Verify `models/utils.py` has all required helper functions:
- ✅ `_get_place(endpoint_id, place_uuid)` - already exists
- ✅ `_get_corporation_profile(endpoint_id, corporation_uuid)` - already exists
- ✅ `_get_data(endpoint_id, data_identity, data_type)` - already exists
- ✅ `_get_contact_profile(endpoint_id, contact_uuid)` - already exists

**Action:** No changes needed - all utilities already exist.

#### 1.3 Create Backup Tests
**Purpose:** Ensure we can verify no regressions after migration

```bash
# Run existing tests and capture baseline
python -m pytest ai_marketing_engine/tests/ -v --tb=short > test_baseline_before_migration.log
```

**Action Items:**
- [ ] Run full test suite
- [ ] Document current GraphQL schema (generate SDL)
- [ ] Capture sample queries and their responses

---

### Phase 2: Update GraphQL Types (Core Changes)
**Goal:** Convert GraphQL types to use nested field resolvers

#### 2.1 Update `types/corporation_profile.py`

**Changes:**
- Keep `data` as `JSON()` but add resolver `resolve_data`
- Move data fetching from `get_corporation_profile_type` to resolver

**File:** `ai_marketing_engine/types/corporation_profile.py`

```python
#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import print_function

__author__ = "bibow"

from graphene import DateTime, List, ObjectType, String

from silvaengine_dynamodb_base import ListObjectType
from silvaengine_utility import JSON

from ..models.utils import _get_data


class CorporationProfileType(ObjectType):
    endpoint_id = String()
    corporation_uuid = String()
    external_id = String()
    corporation_type = String()
    business_name = String()
    categories = List(String)
    address = JSON()  # Keep as JSON since it's a MapAttribute

    # Dynamic attributes bag – still JSON, but lazily resolved
    data = JSON()

    updated_by = String()
    created_at = DateTime()
    updated_at = DateTime()

    # ------- Nested / dynamic resolvers -------

    def resolve_data(parent, info):
        """
        Resolve dynamic attributes for corporation profiles on demand.
        Uses AttributeValueModel via _get_data(..., "corporation").
        """
        endpoint_id = getattr(parent, "endpoint_id", None)
        corporation_uuid = getattr(parent, "corporation_uuid", None)
        if not endpoint_id or not corporation_uuid:
            return None

        return _get_data(endpoint_id, corporation_uuid, "corporation")


class CorporationProfileListType(ListObjectType):
    corporation_profile_list = List(CorporationProfileType)
```

**Breaking Changes:** None - backward compatible since `data` is still available

---

#### 2.2 Update `types/place.py`

**Changes:**
- Convert `corporation_profile` from `JSON()` to `Field(CorporationProfileType)`
- Add `corporation_uuid` as scalar field (to keep raw ID visible)
- Add `resolve_corporation_profile` resolver

**File:** `ai_marketing_engine/types/place.py`

```python
#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import print_function

__author__ = "bibow"

from graphene import DateTime, List, ObjectType, String, Field

from silvaengine_dynamodb_base import ListObjectType

from ..models.utils import _get_corporation_profile
from .corporation_profile import CorporationProfileType


class PlaceType(ObjectType):
    endpoint_id = String()
    place_uuid = String()
    region = String()
    latitude = String()
    longitude = String()
    business_name = String()
    address = String()
    phone_number = String()
    website = String()
    types = List(String)

    # Nested resolver: strongly-typed nested relationship
    corporation_uuid = String()  # keep raw id
    corporation_profile = Field(lambda: CorporationProfileType)

    updated_by = String()
    updated_at = DateTime()
    created_at = DateTime()

    # ------- Nested resolvers -------

    def resolve_corporation_profile(parent, info):
        """
        Resolve nested corporation profile.

        Works in two cases:
        1) Place came from get_place_type -> has corporation_uuid
        2) Place came from _get_place -> already has corporation_profile dict
        """
        # Case 2: already embedded (e.g., via _get_place)
        existing = getattr(parent, "corporation_profile", None)
        if isinstance(existing, dict):
            return CorporationProfileType(**existing)
        if isinstance(existing, CorporationProfileType):
            return existing

        # Case 1: need to fetch by endpoint_id + corporation_uuid
        endpoint_id = getattr(parent, "endpoint_id", None)
        corporation_uuid = getattr(parent, "corporation_uuid", None)
        if not endpoint_id or not corporation_uuid:
            return None

        corp_dict = _get_corporation_profile(endpoint_id, corporation_uuid)
        if not corp_dict:
            return None
        return CorporationProfileType(**corp_dict)


class PlaceListType(ListObjectType):
    place_list = List(PlaceType)
```

**Breaking Changes:**
- GraphQL schema changes: `corporation_profile` type changes from `JSON` to `CorporationProfileType`
- Clients querying `corporation_profile` need to specify nested fields instead of receiving flat JSON
- **Migration Impact:** **MEDIUM** - Requires client query updates

**Client Migration Example:**
```graphql
# OLD (before nested resolvers)
{
  place_list {
    place_list {
      business_name
      corporation_profile  # Returns JSON object
    }
  }
}

# NEW (after nested resolvers)
{
  place_list {
    place_list {
      business_name
      corporation_uuid  # Raw ID still available
      corporation_profile {  # Now strongly typed
        business_name
        external_id
        corporation_type
      }
    }
  }
}
```

---

#### 2.3 Update `types/contact_profile.py`

**Changes:**
- Convert `place` from `JSON()` to `Field(PlaceType)`
- Add `place_uuid` as scalar field
- Add `resolve_place` and `resolve_data` resolvers

**File:** `ai_marketing_engine/types/contact_profile.py`

```python
#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import print_function

__author__ = "bibow"

from graphene import DateTime, List, ObjectType, String, Field

from silvaengine_dynamodb_base import ListObjectType
from silvaengine_utility import JSON

from ..models.utils import _get_place, _get_data
from .place import PlaceType


class ContactProfileType(ObjectType):
    endpoint_id = String()
    contact_uuid = String()
    email = String()
    first_name = String()
    last_name = String()

    # Nested resolver: strongly-typed nested place
    place_uuid = String()
    place = Field(lambda: PlaceType)

    # Dynamic attributes for contact – keep as JSON, resolved lazily
    data = JSON()

    updated_by = String()
    created_at = DateTime()
    updated_at = DateTime()

    # ------- Nested resolvers -------

    def resolve_place(parent, info):
        """
        Resolve nested Place for this contact_profile.
        Uses utils._get_place so existing behavior is preserved.
        """
        endpoint_id = getattr(parent, "endpoint_id", None)
        place_uuid = getattr(parent, "place_uuid", None)
        if not endpoint_id or not place_uuid:
            return None

        place_dict = _get_place(endpoint_id, place_uuid)
        if not place_dict:
            return None

        # Wrap dict into PlaceType so its own nested resolvers work
        return PlaceType(**place_dict)

    def resolve_data(parent, info):
        """
        Resolve dynamic attributes for contact profiles on demand.
        Uses AttributeValueModel via _get_data(..., "contact").
        """
        endpoint_id = getattr(parent, "endpoint_id", None)
        contact_uuid = getattr(parent, "contact_uuid", None)
        if not endpoint_id or not contact_uuid:
            return None

        return _get_data(endpoint_id, contact_uuid, "contact")


class ContactProfileListType(ListObjectType):
    contact_profile_list = List(ContactProfileType)
```

**Breaking Changes:**
- GraphQL schema changes: `place` type changes from `JSON` to `PlaceType`
- **Migration Impact:** **HIGH** - Requires client query updates

---

#### 2.4 Update `types/contact_request.py`

**Changes:**
- Convert `contact_profile` from `JSON()` to `Field(ContactProfileType)`
- Add `contact_uuid` and `place_uuid` as scalar fields
- Add `resolve_contact_profile` resolver

**File:** `ai_marketing_engine/types/contact_request.py`

```python
#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import print_function

__author__ = "bibow"

from graphene import DateTime, List, ObjectType, String, Field

from silvaengine_dynamodb_base import ListObjectType

from ..models.utils import _get_contact_profile
from .contact_profile import ContactProfileType


class ContactRequestType(ObjectType):
    endpoint_id = String()
    request_uuid = String()
    request_title = String()
    request_detail = String()
    
    # Nested resolver: strongly-typed nested relationship
    contact_uuid = String()  # keep raw id
    place_uuid = String()     # keep raw id
    contact_profile = Field(lambda: ContactProfileType)
    
    updated_by = String()
    created_at = DateTime()
    updated_at = DateTime()

    # ------- Nested resolvers -------

    def resolve_contact_profile(parent, info):
        """
        Resolve nested contact profile.
        
        Works in two cases:
        1) ContactRequest came from get_contact_request_type -> has contact_uuid
        2) ContactRequest came from elsewhere -> already has contact_profile dict
        """
        # Case 2: already embedded
        existing = getattr(parent, "contact_profile", None)
        if isinstance(existing, dict):
            return ContactProfileType(**existing)
        if isinstance(existing, ContactProfileType):
            return existing

        # Case 1: need to fetch by endpoint_id + contact_uuid
        endpoint_id = getattr(parent, "endpoint_id", None)
        contact_uuid = getattr(parent, "contact_uuid", None)
        if not endpoint_id or not contact_uuid:
            return None

        contact_dict = _get_contact_profile(endpoint_id, contact_uuid)
        if not contact_dict:
            return None
        return ContactProfileType(**contact_dict)


class ContactRequestListType(ListObjectType):
    contact_request_list = List(ContactRequestType)
```

**Breaking Changes:**
- GraphQL schema changes: `contact_profile` type changes from `JSON` to `ContactProfileType`
- **Migration Impact:** **HIGH** - Requires client query updates
- **Note:** This creates a 4-level nesting chain: ContactRequest → ContactProfile → Place → CorporationProfile

---

### Phase 3: Update Model Type Converters
**Goal:** Simplify `get_*_type` functions to return minimal data

#### 3.1 Update `models/corporation_profile.py`

**Current Implementation:**
```python
def get_corporation_profile_type(
    info: ResolveInfo, corporation_profile: CorporationProfileModel
) -> CorporationProfileType:
    try:
        data = _get_data(
            corporation_profile.endpoint_id,
            corporation_profile.corporation_uuid,
            "corporation",
        )
        corporation_profile = corporation_profile.__dict__["attribute_values"]
        corporation_profile["data"] = data  # ← Remove this
    except Exception as e:
        log = traceback.format_exc()
        info.context.get("logger").exception(log)
        raise e
    return CorporationProfileType(**Utility.json_normalize(corporation_profile))
```

**New Implementation:**
```python
def get_corporation_profile_type(
    info: ResolveInfo, corporation_profile: CorporationProfileModel
) -> CorporationProfileType:
    """
    Nested resolver approach: return minimal corporation_profile data.
    - Do NOT embed 'data' here anymore.
    'data' is resolved lazily by CorporationProfileType.resolve_data.
    """
    try:
        corp_dict = corporation_profile.__dict__["attribute_values"]
    except Exception:
        log = traceback.format_exc()
        info.context.get("logger").exception(log)
        raise

    return CorporationProfileType(**Utility.json_normalize(corp_dict))
```

**Changes:**
- Remove `_get_data()` call
- Remove `corporation_profile["data"] = data` line
- Simplify to just return normalized attributes

---

#### 3.2 Update `models/place.py`

**Current Implementation:**
```python
def get_place_type(info: ResolveInfo, place: PlaceModel) -> PlaceType:
    try:
        corporation_profile = None
        if place.corporation_uuid:
            corporation_profile = _get_corporation_profile(
                place.endpoint_id,
                place.corporation_uuid,
            )
        place = place.__dict__["attribute_values"]
        if corporation_profile:
            place["corporation_profile"] = corporation_profile  # ← Remove this
            place.pop("corporation_uuid")  # ← Remove this
    except Exception as e:
        log = traceback.format_exc()
        info.context.get("logger").exception(log)
        raise e

    return PlaceType(**Utility.json_normalize(place))
```

**New Implementation:**
```python
def get_place_type(info: ResolveInfo, place: PlaceModel) -> PlaceType:
    """
    Nested resolver approach: return a minimal PlaceType, without embedding corporation_profile.
    Nested corporation_profile is resolved by PlaceType.resolve_corporation_profile.
    """
    try:
        place_dict = place.__dict__["attribute_values"]
    except Exception:
        log = traceback.format_exc()
        info.context.get("logger").exception(log)
        raise

    return PlaceType(**Utility.json_normalize(place_dict))
```

**Changes:**
- Remove `_get_corporation_profile()` call
- Remove `corporation_profile` embedding logic
- Keep `corporation_uuid` in the dict (don't pop it)

---

#### 3.3 Update `models/contact_profile.py`

**Current Implementation:**
```python
def get_contact_profile_type(
    info: ResolveInfo, contact_profile: ContactProfileModel
) -> ContactProfileType:
    try:
        place = _get_place(contact_profile.endpoint_id, contact_profile.place_uuid)
        data = _get_data(
            contact_profile.endpoint_id, contact_profile.contact_uuid, "contact"
        )
        contact_profile = contact_profile.__dict__["attribute_values"]
        contact_profile["place"] = place  # ← Remove this
        contact_profile.pop("place_uuid")  # ← Remove this
        contact_profile["data"] = data  # ← Remove this
    except Exception as e:
        log = traceback.format_exc()
        info.context.get("logger").exception(log)
        raise e

    return ContactProfileType(**Utility.json_normalize(contact_profile))
```

**New Implementation:**
```python
def get_contact_profile_type(
    info: ResolveInfo, contact_profile: ContactProfileModel
) -> ContactProfileType:
    """
    Nested resolver approach: return minimal contact_profile data.
    - Do NOT embed 'place'
    - Do NOT embed 'data'
    Those are resolved lazily by ContactProfileType resolvers.
    """
    try:
        cp_dict = contact_profile.__dict__["attribute_values"]
    except Exception:
        log = traceback.format_exc()
        info.context.get("logger").exception(log)
        raise

    return ContactProfileType(**Utility.json_normalize(cp_dict))
```

**Changes:**
- Remove `_get_place()` call
- Remove `_get_data()` call
- Remove all embedding logic
- Keep `place_uuid` in the dict (don't pop it)

---

#### 3.4 Update `models/contact_request.py`

**Current Implementation:**
```python
def get_contact_request_type(
    info: ResolveInfo, contact_request: ContactRequestModel
) -> ContactRequestType:
    try:
        contact_profile = _get_contact_profile(
            contact_request.endpoint_id, contact_request.contact_uuid
        )
        contact_request = contact_request.__dict__["attribute_values"]
        contact_request["contact_profile"] = contact_profile  # ← Remove this
        contact_request.pop("place_uuid")  # ← Remove this
        contact_request.pop("contact_uuid")  # ← Remove this
    except Exception as e:
        log = traceback.format_exc()
        info.context.get("logger").exception(log)
        raise e
    return ContactRequestType(**Utility.json_normalize(contact_request))
```

**New Implementation:**
```python
def get_contact_request_type(
    info: ResolveInfo, contact_request: ContactRequestModel
) -> ContactRequestType:
    """
    Nested resolver approach: return minimal contact_request data.
    - Do NOT embed 'contact_profile'
    That is resolved lazily by ContactRequestType.resolve_contact_profile.
    """
    try:
        cr_dict = contact_request.__dict__["attribute_values"]
    except Exception:
        log = traceback.format_exc()
        info.context.get("logger").exception(log)
        raise

    return ContactRequestType(**Utility.json_normalize(cr_dict))
```

**Changes:**
- Remove `_get_contact_profile()` call
- Remove embedding logic
- Keep `contact_uuid` and `place_uuid` in dict (don't pop them)

---

### Phase 4: Testing & Validation

#### 4.1 Unit Tests
Create/update tests for each resolver:

**File:** `ai_marketing_engine/tests/test_nested_resolvers.py` (new file)

```python
#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Tests for nested resolvers"""

import pytest
from unittest.mock import Mock, patch
from ai_marketing_engine.types.contact_profile import ContactProfileType
from ai_marketing_engine.types.contact_request import ContactRequestType
from ai_marketing_engine.types.place import PlaceType
from ai_marketing_engine.types.corporation_profile import CorporationProfileType


class TestContactProfileResolvers:
    """Test ContactProfileType resolvers"""
    
    def test_resolve_place_with_valid_data(self):
        """Test place resolver returns PlaceType when data exists"""
        parent = Mock(endpoint_id="test-endpoint", place_uuid="place-123")
        info = Mock()
        
        with patch('ai_marketing_engine.types.contact_profile._get_place') as mock_get:
            mock_get.return_value = {
                "place_uuid": "place-123",
                "business_name": "Test Business"
            }
            
            result = ContactProfileType.resolve_place(parent, info)
            
            assert isinstance(result, PlaceType)
            assert result.place_uuid == "place-123"
            mock_get.assert_called_once_with("test-endpoint", "place-123")
    
    def test_resolve_place_with_missing_data(self):
        """Test place resolver returns None when place not found"""
        parent = Mock(endpoint_id="test-endpoint", place_uuid=None)
        info = Mock()
        
        result = ContactProfileType.resolve_place(parent, info)
        
        assert result is None
    
    def test_resolve_data(self):
        """Test data resolver fetches dynamic attributes"""
        parent = Mock(endpoint_id="test-endpoint", contact_uuid="contact-123")
        info = Mock()
        
        with patch('ai_marketing_engine.types.contact_profile._get_data') as mock_get:
            mock_get.return_value = {"custom_field": "value"}
            
            result = ContactProfileType.resolve_data(parent, info)
            
            assert result == {"custom_field": "value"}
            mock_get.assert_called_once_with("test-endpoint", "contact-123", "contact")


class TestContactRequestResolvers:
    """Test ContactRequestType resolvers"""
    
    def test_resolve_contact_profile_with_existing_dict(self):
        """Test resolver handles pre-embedded contact_profile dict"""
        parent = Mock(
            contact_profile={"contact_uuid": "contact-123", "email": "test@example.com"}
        )
        info = Mock()
        
        result = ContactRequestType.resolve_contact_profile(parent, info)
        
        assert isinstance(result, ContactProfileType)
    
    def test_resolve_contact_profile_fetch_on_demand(self):
        """Test resolver fetches contact when only UUID available"""
        parent = Mock(
            endpoint_id="test-endpoint",
            contact_uuid="contact-123"
        )
        # Remove contact_profile attribute
        delattr(parent, 'contact_profile')
        info = Mock()
        
        with patch('ai_marketing_engine.types.contact_request._get_contact_profile') as mock_get:
            mock_get.return_value = {
                "contact_uuid": "contact-123",
                "email": "test@example.com"
            }
            
            result = ContactRequestType.resolve_contact_profile(parent, info)
            
            assert isinstance(result, ContactProfileType)
            mock_get.assert_called_once_with("test-endpoint", "contact-123")


class TestPlaceResolvers:
    """Test PlaceType resolvers"""
    
    def test_resolve_corporation_profile_with_existing_dict(self):
        """Test resolver handles pre-embedded corporation_profile dict"""
        parent = Mock(
            corporation_profile={"corporation_uuid": "corp-123", "business_name": "Corp"}
        )
        info = Mock()
        
        result = PlaceType.resolve_corporation_profile(parent, info)
        
        assert isinstance(result, CorporationProfileType)
    
    def test_resolve_corporation_profile_fetch_on_demand(self):
        """Test resolver fetches corporation when only UUID available"""
        parent = Mock(
            endpoint_id="test-endpoint",
            corporation_uuid="corp-123"
        )
        # Remove corporation_profile attribute
        delattr(parent, 'corporation_profile')
        info = Mock()
        
        with patch('ai_marketing_engine.types.place._get_corporation_profile') as mock_get:
            mock_get.return_value = {
                "corporation_uuid": "corp-123",
                "business_name": "Corp"
            }
            
            result = PlaceType.resolve_corporation_profile(parent, info)
            
            assert isinstance(result, CorporationProfileType)
            mock_get.assert_called_once_with("test-endpoint", "corp-123")


class TestCorporationProfileResolvers:
    """Test CorporationProfileType resolvers"""
    
    def test_resolve_data(self):
        """Test data resolver fetches dynamic attributes"""
        parent = Mock(endpoint_id="test-endpoint", corporation_uuid="corp-123")
        info = Mock()
        
        with patch('ai_marketing_engine.types.corporation_profile._get_data') as mock_get:
            mock_get.return_value = {"industry": "tech"}
            
            result = CorporationProfileType.resolve_data(parent, info)
            
            assert result == {"industry": "tech"}
            mock_get.assert_called_once_with("test-endpoint", "corp-123", "corporation")
```

**Action Items:**
- [ ] Create test file
- [ ] Run tests: `pytest ai_marketing_engine/tests/test_nested_resolvers.py -v`
- [ ] Ensure 100% coverage for all resolvers

---

#### 4.2 Integration Tests

**Update existing tests:**

```python
# ai_marketing_engine/tests/test_ai_marketing_engine.py

def test_contact_profile_with_nested_place(graphql_client):
    """Test that nested place resolves correctly"""
    query = '''
    query {
        contact_profile_list(limit: 1) {
            contact_profile_list {
                contact_uuid
                email
                place_uuid
                place {
                    business_name
                    corporation_uuid
                    corporation_profile {
                        business_name
                        external_id
                    }
                }
                data
            }
        }
    }
    '''
    
    result = graphql_client.execute(query)
    
    assert 'errors' not in result
    assert result['data']['contact_profile_list']['contact_profile_list']
    
    # Verify nested structure
    contact = result['data']['contact_profile_list']['contact_profile_list'][0]
    assert 'place_uuid' in contact  # Raw ID available
    assert contact['place'] is not None
    assert 'business_name' in contact['place']
    
    # Verify doubly-nested corporation
    if contact['place']['corporation_uuid']:
        assert contact['place']['corporation_profile'] is not None


def test_contact_request_with_deep_nesting(graphql_client):
    """Test 4-level nesting: ContactRequest → ContactProfile → Place → CorporationProfile"""
    query = '''
    query {
        contact_request_list(limit: 1) {
            contact_request_list {
                request_uuid
                contact_uuid
                contact_profile {
                    email
                    place_uuid
                    place {
                        business_name
                        corporation_profile {
                            business_name
                        }
                    }
                }
            }
        }
    }
    '''
    
    result = graphql_client.execute(query)
    
    assert 'errors' not in result
    request = result['data']['contact_request_list']['contact_request_list'][0]
    assert 'contact_uuid' in request  # Raw ID available
    assert request['contact_profile'] is not None
```

**Action Items:**
- [ ] Update existing GraphQL queries in tests
- [ ] Add tests for all nesting levels (up to 4 levels)
- [ ] Test queries that don't request nested fields (lazy loading verification)

---

#### 4.3 Performance Tests

**Create performance comparison:**

```python
# ai_marketing_engine/tests/test_performance_nested_resolvers.py

import time
import pytest

def test_list_performance_without_nested_fields(graphql_client):
    """Verify queries without nested fields are faster (no unnecessary fetches)"""
    query = '''
    query {
        contact_profile_list(limit: 100) {
            contact_profile_list {
                contact_uuid
                email
                # Note: NOT requesting place or data
            }
        }
    }
    '''
    
    start = time.time()
    result = graphql_client.execute(query)
    duration = time.time() - start
    
    assert 'errors' not in result
    # Should be fast since no nested resolvers are triggered
    assert duration < 1.0  # Adjust threshold as needed


def test_list_performance_with_nested_fields(graphql_client):
    """Verify nested field fetching only happens when requested"""
    query_with_nesting = '''
    query {
        contact_profile_list(limit: 100) {
            contact_profile_list {
                contact_uuid
                email
                place {
                    business_name
                }
                data
            }
        }
    }
    '''
    
    start = time.time()
    result = graphql_client.execute(query_with_nesting)
    duration = time.time() - start
    
    assert 'errors' not in result
    # Will be slower but acceptable
    # Document the acceptable range
    print(f"Query with nesting took {duration:.2f}s for 100 items")


def test_deep_nesting_performance(graphql_client):
    """Test performance of 4-level nesting"""
    query = '''
    query {
        contact_request_list(limit: 10) {
            contact_request_list {
                request_uuid
                contact_profile {
                    email
                    place {
                        business_name
                        corporation_profile {
                            business_name
                        }
                    }
                }
            }
        }
    }
    '''
    
    start = time.time()
    result = graphql_client.execute(query)
    duration = time.time() - start
    
    assert 'errors' not in result
    print(f"Deep nesting (4 levels) took {duration:.2f}s for 10 items")
```

---

### Phase 5: Update Utils Functions (Compatibility)

#### 5.1 Review `models/utils.py` Functions

**Current behavior of `_get_place`:**
- Returns dict with embedded `corporation_profile`

**Nested resolver requirement:**
- Can continue returning embedded data OR return minimal data
- The resolver will handle both cases

**Action:** Keep current implementation as-is. The resolver `PlaceType.resolve_corporation_profile` already handles both cases:
```python
# Case 2: already embedded (e.g., via _get_place)
existing = getattr(parent, "corporation_profile", None)
if isinstance(existing, dict):
    return CorporationProfileType(**existing)
```

**No changes needed** to `_get_place`, `_get_corporation_profile`, or `_get_contact_profile` in utils.

---

### Phase 6: Documentation & Migration Guide

#### 6.1 Generate Updated GraphQL Schema

```bash
# Use graphene to export schema
python -c "
from ai_marketing_engine.schema import schema
print(schema.introspect())
" > schema_nested_resolvers.graphql
```

#### 6.2 Create Client Migration Guide

**File:** `docs/CLIENT_MIGRATION_GUIDE.md`

```markdown
# Client Migration Guide: Nested Resolvers

## Overview
The GraphQL API has been updated to use strongly-typed nested resolvers instead of JSON scalars for related entities.

## Breaking Changes

### 1. `contact_profile` field in ContactRequestType
**Before:**
```graphql
type ContactRequestType {
  contact_profile: JSON
}
```

**After:**
```graphql
type ContactRequestType {
  contact_uuid: String
  place_uuid: String
  contact_profile: ContactProfileType
}
```

### 2. `place` field in ContactProfileType
**Before:**
```graphql
type ContactProfileType {
  place: JSON
}
```

**After:**
```graphql
type ContactProfileType {
  place_uuid: String
  place: PlaceType
}
```

**Migration:**
```graphql
# OLD QUERY
{
  contact_profile_list {
    contact_profile_list {
      place  # Returns flat JSON
    }
  }
}

# NEW QUERY
{
  contact_profile_list {
    contact_profile_list {
      place_uuid  # Raw ID
      place {     # Nested object
        business_name
        address
      }
    }
  }
}
```

### 3. `corporation_profile` field in PlaceType
**Before:**
```graphql
type PlaceType {
  corporation_profile: JSON
}
```

**After:**
```graphql
type PlaceType {
  corporation_uuid: String
  corporation_profile: CorporationProfileType
}
```

### 4. `data` fields (ContactProfile, CorporationProfile)
**No breaking changes** - still JSON, but now resolved lazily.

## Benefits for Clients

1. **Type Safety**: IDE autocomplete and type checking for nested fields
2. **Flexible Queries**: Only request the fields you need
3. **Better Performance**: Don't fetch nested data you don't use
4. **GraphQL Fragments**: Can use fragments on typed objects

## Example: Deeply Nested Query (4 levels)
```graphql
{
  contact_request_list {
    contact_request_list {
      request_title
      contact_profile {
        email
        place {
          business_name
          corporation_profile {
            business_name
            categories
          }
        }
      }
    }
  }
}
```

## Performance Optimization

### Fast Query (No Nesting)
```graphql
{
  contact_profile_list(limit: 100) {
    contact_profile_list {
      contact_uuid
      email
      place_uuid  # Just the ID, no fetching
    }
  }
}
```

### Selective Nesting
```graphql
{
  place_list(region: "US-CA") {
    place_list {
      place_uuid
      business_name
      corporation_uuid  # Just the ID
      # Note: NOT requesting corporation_profile
    }
  }
}
```
Only the fields you request will trigger database fetches.
```

---

### Phase 7: Deployment Strategy

#### 7.1 Staged Rollout Plan

**Option A: Big Bang (Recommended for internal APIs)**
1. Deploy all changes at once
2. Update all clients simultaneously
3. Requires coordination but cleaner

**Option B: Gradual Migration (Recommended for external APIs)**
1. Deploy backend changes (backward compatible)
2. Gradually update clients to use new schema
3. Eventually deprecate old behavior

**For this project:** Use **Option A** since you control all clients.

#### 7.2 Deployment Checklist

**Pre-Deployment:**
- [ ] All tests passing
- [ ] Performance benchmarks acceptable
- [ ] Client migration guide published
- [ ] Rollback plan documented

**Deployment:**
- [ ] Deploy to staging environment
- [ ] Run integration tests against staging
- [ ] Update client applications
- [ ] Deploy to production
- [ ] Monitor error rates and performance

**Post-Deployment:**
- [ ] Verify all queries working
- [ ] Check CloudWatch logs for errors
- [ ] Monitor DynamoDB read capacity
- [ ] Validate performance improvements

---

## Risk Assessment

### Low Risk
- ✅ `CorporationProfileType.resolve_data` - Only changes internal behavior
- ✅ Model type converter changes - Transparent to clients
- ✅ Utils functions - No changes needed

### Medium Risk
- ⚠️ `PlaceType.corporation_profile` - Schema change but resolver handles both cases
- ⚠️ Performance - Lazy loading might cause N+1 queries in some cases

### High Risk
- 🔴 `ContactProfileType.place` - Major schema change requiring client updates
- 🔴 `ContactRequestType.contact_profile` - Major schema change requiring client updates
- 🔴 Breaking changes to existing client queries

### Mitigation Strategies

**For N+1 Query Risk:**
- Implement DataLoader pattern if needed
- Monitor query performance
- Add caching layer for frequently accessed nested data

**For Client Breaking Changes:**
- Comprehensive testing before deployment
- Clear migration documentation
- Coordinate with all API consumers

---

## Rollback Plan

### If Issues Detected Post-Deployment:

**Step 1: Immediate Rollback**
```bash
git revert <migration-commit-hash>
git push origin main
# Redeploy previous version
```

**Step 2: Revert Database Changes**
- No database schema changes in this migration
- All changes are code-level only

**Step 3: Notify Clients**
- If clients updated queries, they need to revert

---

## Timeline Estimate

| Phase | Estimated Time | Dependencies |
|-------|---------------|--------------|
| Phase 1: Preparation | 2 hours | None |
| Phase 2: Update Types | 4 hours | Phase 1 |
| Phase 3: Update Models | 3 hours | Phase 2 |
| Phase 4: Testing | 5 hours | Phase 3 |
| Phase 5: Utils Review | 1 hour | Phase 4 |
| Phase 6: Documentation | 2 hours | Phase 5 |
| Phase 7: Deployment | 3 hours | Phase 6 |
| **Total** | **20 hours** | |

**Recommended Schedule:**
- Day 1: Phases 1-3 (implementation)
- Day 2: Phase 4 (testing)
- Day 3: Phases 5-7 (docs + deployment)

---

## Success Criteria

### Must Have
- ✅ All existing tests passing
- ✅ New resolver tests with 100% coverage
- ✅ No increase in error rates post-deployment
- ✅ Client migration guide complete

### Should Have
- ✅ Performance improvement for queries without nested fields
- ✅ Reduced DynamoDB read capacity for simple queries
- ✅ SDL schema documentation updated

### Nice to Have
- ✅ DataLoader implementation for batch loading
- ✅ Query complexity analysis
- ✅ Automated performance regression tests

---

## Appendix A: File Change Summary

### Files to Modify (Core)
1. `ai_marketing_engine/types/corporation_profile.py` - Add `resolve_data`
2. `ai_marketing_engine/types/place.py` - Add `corporation_uuid`, `resolve_corporation_profile`
3. `ai_marketing_engine/types/contact_profile.py` - Add `place_uuid`, `resolve_place`, `resolve_data`
4. `ai_marketing_engine/types/contact_request.py` - Add `contact_uuid`, `place_uuid`, `resolve_contact_profile`
5. `ai_marketing_engine/models/corporation_profile.py` - Simplify `get_corporation_profile_type`
6. `ai_marketing_engine/models/place.py` - Simplify `get_place_type`
7. `ai_marketing_engine/models/contact_profile.py` - Simplify `get_contact_profile_type`
8. `ai_marketing_engine/models/contact_request.py` - Simplify `get_contact_request_type`

### Files to Create (New)
1. `ai_marketing_engine/tests/test_nested_resolvers.py` - Unit tests for resolvers
2. `ai_marketing_engine/tests/test_performance_nested_resolvers.py` - Performance tests
3. `docs/CLIENT_MIGRATION_GUIDE.md` - Client migration guide

### Files to Review (No Changes)
1. `ai_marketing_engine/models/utils.py` - Verify compatibility
2. `ai_marketing_engine/schema.py` - Verify schema registration

---

## Appendix B: Example Queries

### Query 1: Contact Profile with Minimal Data (Fast)
```graphql
query {
  contact_profile_list(limit: 100) {
    contact_profile_list {
      contact_uuid
      email
      place_uuid  # Just the ID, no fetching
    }
  }
}
```
**Performance:** Fast - no nested resolvers triggered

### Query 2: Contact Profile with Full Nesting (Complete)
```graphql
query {
  contact_profile(contact_uuid: "123") {
    contact_uuid
    email
    place {
      business_name
      address
      corporation_profile {
        business_name
        categories
        data  # Dynamic attributes
      }
    }
    data  # Dynamic attributes
  }
}
```
**Performance:** Slower but complete - all nested data resolved

### Query 3: Contact Request with Deep Nesting (4 levels)
```graphql
query {
  contact_request_list(limit: 10) {
    contact_request_list {
      request_uuid
      request_title
      contact_uuid  # Raw ID
      contact_profile {
        email
        place {
          business_name
          corporation_profile {
            business_name
          }
        }
      }
    }
  }
}
```
**Performance:** Slowest - 4 levels of nesting, but demonstrates flexibility

### Query 4: Place List with Selective Nesting
```graphql
query {
  place_list(region: "US-CA") {
    place_list {
      place_uuid
      business_name
      corporation_uuid  # Just the ID
      # Note: NOT requesting corporation_profile
    }
  }
}
```
**Performance:** Fast - corporation_profile not fetched

---

## Appendix C: Models Without Nested Relationships

The following models do NOT require changes as they have no nested entity relationships:

1. **ActivityHistoryType** - Only primitives and `data_diff` (JSON is fine for unstructured data)
2. **QuestionGroupType** - Only primitives and `question_criteria` (JSON is fine)
3. **AttributeValueType** - No nested relationships
4. **UTMTagDataCollectionType** - No nested relationships

These types already follow best practices by using JSON only for truly dynamic/unstructured data.

---

## N+1 Query Pattern Analysis

### Overview
After thorough code review, **N+1 query patterns have been identified** in the current nested resolver implementation. This section documents the issues and provides mitigation strategies.

### What is the N+1 Problem?
The N+1 problem occurs when:
1. You fetch N parent records (1 query)
2. For each parent, you fetch related data in separate queries (N queries)
3. Total: 1 + N queries instead of 1-2 optimized queries

### Identified N+1 Issues in Current Implementation

#### 🔴 Issue #1: ContactProfileType.resolve_place
**Location:** [types/contact_profile.py:36-51](ai_marketing_engine/types/contact_profile.py#L36-L51)

**Problem:**
```graphql
query {
  contact_profile_list(limit: 100) {
    contact_profile_list {
      email
      place {  # N+1 ISSUE HERE
        business_name
      }
    }
  }
}
```

**What Happens:**
1. Query fetches 100 contact profiles (1 query to `ContactProfileModel`)
2. For each contact, `resolve_place` calls `_get_place()` → `PlaceModel.get()` (100 queries)
3. **Total: 101 DynamoDB queries**

**Code Path:**
```
resolve_contact_profile_list
  → ContactProfileModel.query (1 query)
  → For each result: ContactProfileType.resolve_place
    → _get_place (100 individual queries)
      → PlaceModel.get (100 DynamoDB GetItem operations)
```

#### 🔴 Issue #2: ContactProfileType.resolve_data
**Location:** [types/contact_profile.py:53-63](ai_marketing_engine/types/contact_profile.py#L53-L63)

**Problem:**
```graphql
query {
  contact_profile_list(limit: 100) {
    contact_profile_list {
      email
      data {  # N+1 ISSUE HERE
        custom_field
      }
    }
  }
}
```

**What Happens:**
1. Query fetches 100 contact profiles (1 query)
2. For each contact, `resolve_data` calls `_get_data()` → queries `AttributeValueModel` (100 queries)
3. **Total: 101 DynamoDB queries**

**Code Path:**
```
resolve_contact_profile_list
  → ContactProfileModel.query (1 query)
  → For each result: ContactProfileType.resolve_data
    → _get_data (100 queries)
      → AttributeValueModel.data_identity_data_type_attribute_name_index.query (100 queries)
```

#### 🔴 Issue #3: PlaceType.resolve_corporation_profile
**Location:** [types/place.py:37-61](ai_marketing_engine/types/place.py#L37-L61)

**Problem:**
```graphql
query {
  place_list(limit: 100) {
    place_list {
      business_name
      corporation_profile {  # N+1 ISSUE HERE
        business_name
      }
    }
  }
}
```

**What Happens:**
1. Query fetches 100 places (1 query)
2. For each place, `resolve_corporation_profile` calls `_get_corporation_profile()` (100 queries)
3. **Total: 101 DynamoDB queries**

#### 🔴 Issue #4: CorporationProfileType.resolve_data
**Location:** [types/corporation_profile.py:33-43](ai_marketing_engine/types/corporation_profile.py#L33-L43)

**Problem:** Same pattern as Issue #2 - N queries to `AttributeValueModel` for dynamic attributes.

#### 🔴🔴 CRITICAL Issue #5: Cascading N+1 with Deep Nesting
**Location:** Multiple resolvers when combined

**Problem:**
```graphql
query {
  contact_profile_list(limit: 10) {
    contact_profile_list {
      email
      place {                        # 10 queries
        business_name
        corporation_profile {         # 10 queries
          business_name
          data                        # 10 queries
        }
      }
      data                            # 10 queries
    }
  }
}
```

**What Happens:**
1. Fetch 10 contacts (1 query)
2. Resolve 10 places (10 queries)
3. Resolve 10 corporation profiles (10 queries)
4. Resolve 10 corporation data (10 queries)
5. Resolve 10 contact data (10 queries)
6. **Total: 41 DynamoDB queries for 10 records!**

**Exponential Growth:**
- 100 contacts with deep nesting: **401 queries**
- 1000 contacts: **4001 queries** 💥

### Impact Assessment

| Scenario | Records | Queries | Performance Impact |
|----------|---------|---------|-------------------|
| Contact list (no nesting) | 100 | 1 | ✅ Excellent |
| Contact list + place | 100 | 101 | ⚠️ Poor (10x slower) |
| Contact list + place + corp | 100 | 201 | 🔴 Very Poor (20x slower) |
| Contact list (full nesting) | 100 | 401 | 💥 Unacceptable (40x slower) |
| Contact list (full nesting) | 1000 | 4001 | 💥💥 System crash risk |

### Why This Happens

The current resolvers use **individual `get()` operations**:
```python
def _get_place(endpoint_id: str, place_uuid: str) -> Dict[str, Any]:
    # ...
    place = get_place(endpoint_id, place_uuid)  # ← Individual GetItem
```

```python
def _get_data(endpoint_id: str, data_identity: str, data_type: str) -> Dict[str, Any]:
    results = AttributeValueModel.data_identity_data_type_attribute_name_index.query(
        hash_key=data_identity,  # ← Individual query per identity
        # ...
    )
```

**Each resolver call triggers a separate DynamoDB operation.**

### Solution: Batch Loading with DataLoader Pattern

**What is DataLoader?**
- Batches multiple requests into a single query
- Deduplicates requests
- Caches results within a single GraphQL request

**Implementation Plan:**

Create [models/batch_loaders.py](ai_marketing_engine/models/batch_loaders.py):
```python
from typing import Dict, List, Optional, Any
from collections import defaultdict

class BatchLoader:
    """Base class for batch loading entities to prevent N+1 queries."""
    
    def __init__(self):
        self._batch_cache: Dict[str, Any] = {}
        self._pending_ids: Dict[str, set] = defaultdict(set)
    
    def add_pending_id(self, entity_type: str, entity_id: str) -> None:
        """Add an ID to the pending batch for later resolution."""
        self._pending_ids[entity_type].add(entity_id)
    
    def get_cached(self, entity_type: str, entity_id: str) -> Optional[Any]:
        """Get cached entity if available."""
        cache_key = f"{entity_type}:{entity_id}"
        return self._batch_cache.get(cache_key)
    
    def set_cached(self, entity_type: str, entity_id: str, data: Any) -> None:
        """Cache entity data."""
        cache_key = f"{entity_type}:{entity_id}"
        self._batch_cache[cache_key] = data
    
    def batch_load_places(self, endpoint_id: str, place_uuids: List[str]) -> Dict[str, Dict]:
        """Batch load multiple places using DynamoDB batch_get_item."""
        from .place import PlaceModel
        
        if not place_uuids:
            return {}
        
        # Use DynamoDB batch_get_item for efficient bulk fetching
        results = {}
        batch_keys = [(endpoint_id, place_uuid) for place_uuid in place_uuids]
        
        try:
            # Batch fetch from DynamoDB
            for item in PlaceModel.batch_get(batch_keys):
                place_dict = item.__dict__["attribute_values"]
                # Apply nested corporation_profile if needed
                if item.corporation_uuid:
                    corp_profile = self.get_cached("corporation", item.corporation_uuid)
                    if corp_profile:
                        place_dict["corporation_profile"] = corp_profile
                
                results[item.place_uuid] = place_dict
                self.set_cached("place", item.place_uuid, place_dict)
        
        except Exception as e:
            # Fallback to individual queries if batch fails
            from .utils import _get_place
            for place_uuid in place_uuids:
                try:
                    place_data = _get_place(endpoint_id, place_uuid)
                    if place_data:
                        results[place_uuid] = place_data
                        self.set_cached("place", place_uuid, place_data)
                except Exception:
                    continue
        
        return results
    
    def batch_load_corporations(self, endpoint_id: str, corp_uuids: List[str]) -> Dict[str, Dict]:
        """Batch load multiple corporation profiles."""
        from .corporation_profile import CorporationProfileModel
        
        if not corp_uuids:
            return {}
        
        results = {}
        batch_keys = [(endpoint_id, corp_uuid) for corp_uuid in corp_uuids]
        
        try:
            for item in CorporationProfileModel.batch_get(batch_keys):
                corp_dict = item.__dict__["attribute_values"]
                results[item.corporation_uuid] = corp_dict
                self.set_cached("corporation", item.corporation_uuid, corp_dict)
        except Exception:
            # Fallback to individual queries
            from .utils import _get_corporation_profile
            for corp_uuid in corp_uuids:
                try:
                    corp_data = _get_corporation_profile(endpoint_id, corp_uuid)
                    if corp_data:
                        results[corp_uuid] = corp_data
                        self.set_cached("corporation", corp_uuid, corp_data)
                except Exception:
                    continue
        
        return results
    
    def resolve_pending_batches(self, endpoint_id: str) -> None:
        """Execute all pending batch loads."""
        # Load corporations first (no dependencies)
        if "corporation" in self._pending_ids:
            corp_uuids = list(self._pending_ids["corporation"])
            self.batch_load_corporations(endpoint_id, corp_uuids)
        
        # Load places second (may depend on corporations)
        if "place" in self._pending_ids:
            place_uuids = list(self._pending_ids["place"])
            self.batch_load_places(endpoint_id, place_uuids)
        
        # Clear pending after batch load
        self._pending_ids.clear()


# Global batch loader instance per request
_request_batch_loader = None

def get_batch_loader() -> BatchLoader:
    """Get or create batch loader for current request."""
    global _request_batch_loader
    if _request_batch_loader is None:
        _request_batch_loader = BatchLoader()
    return _request_batch_loader

def clear_batch_loader() -> None:
    """Clear batch loader (call at end of request)."""
    global _request_batch_loader
    _request_batch_loader = None
```

**Update resolvers to use BatchLoader:**

[types/contact_profile.py](ai_marketing_engine/types/contact_profile.py):
```python
def resolve_place(parent, info):
    """Resolve nested Place using batch loader to prevent N+1."""
    from ..models.batch_loaders import get_batch_loader
    
    endpoint_id = getattr(parent, "endpoint_id", None)
    place_uuid = getattr(parent, "place_uuid", None)
    if not endpoint_id or not place_uuid:
        return None
    
    batch_loader = get_batch_loader()
    
    # Check cache first
    cached_place = batch_loader.get_cached("place", place_uuid)
    if cached_place:
        return PlaceType(**cached_place)
    
    # Add to pending batch (will be resolved later)
    batch_loader.add_pending_id("place", place_uuid)
    
    # Trigger batch resolution if this is the first request
    batch_loader.resolve_pending_batches(endpoint_id)
    
    # Get from cache after batch load
    place_dict = batch_loader.get_cached("place", place_uuid)
    if not place_dict:
        return None
    
    return PlaceType(**place_dict)
```

**Benefits:**
- 100 contacts + place: **101 queries → 2 queries** (1 + 1 batch)
- 100 contacts + place + corp: **201 queries → 3 queries** (1 + 1 + 1)
- **40-100x performance improvement** for nested queries

### Implementation Action Plan

**Phase 1: Immediate (Critical)**
1. ✅ Document N+1 issues (this section)
2. 📝 Add monitoring for query counts
3. ⚠️ Add warnings to documentation about list queries with nesting
4. 🔧 Set reasonable limits on list queries (e.g., max 50 with nesting)

**Phase 2: Batch Loader Implementation (2-3 weeks)**
1. 🎯 Implement BatchLoader pattern for Place and CorporationProfile
2. 🧪 Add performance tests comparing before/after
3. 📊 Benchmark improvements
4. 📚 Update documentation with BatchLoader usage

**Phase 3: Complete Integration (1-2 months)**
1. 🎯 Implement BatchLoader for AttributeValue (complex)
2. 📈 Implement query complexity limits
3. 🔍 Add query performance monitoring/alerting
4. 📋 Complete migration to nested resolvers with batch loading

### Temporary Workarounds Until DataLoader is Implemented

**1. Document query limits:**
```graphql
# ❌ BAD: Will cause 401 queries
query {
  contact_profile_list(limit: 100) {
    contact_profile_list {
      place { corporation_profile { data } }
      data
    }
  }
}

# ✅ GOOD: Only 1 query
query {
  contact_profile_list(limit: 100) {
    contact_profile_list {
      contact_uuid
      email
      place_uuid  # Just the ID
    }
  }
}

# ⚠️ ACCEPTABLE: 11 queries for 10 records
query {
  contact_profile_list(limit: 10) {
    contact_profile_list {
      place { business_name }
    }
  }
}
```

**2. Add query complexity limits:**
```python
# schema.py
from graphql import validate
from graphql.validation import NoSchemaIntrospectionCustomRule

def validate_query_complexity(query, max_depth=3, max_complexity=100):
    """Reject queries that are too complex"""
    # Implement complexity calculation
    # Reject if complexity > threshold
```

**3. Use pagination + smaller limits for nested queries:**
```graphql
# Instead of limit: 100, use limit: 10 with nesting
query {
  contact_profile_list(limit: 10, offset: 0) {
    contact_profile_list {
      place { business_name }
    }
  }
}
```

### Testing N+1 Issues

**Add to [tests/test_performance_nested_resolvers.py](ai_marketing_engine/tests/test_performance_nested_resolvers.py):**

```python
import pytest
from unittest.mock import patch, MagicMock

def test_n_plus_one_contact_profile_place():
    """Verify N+1 issue exists (to be fixed with DataLoader)"""
    query = '''
    query {
        contact_profile_list(limit: 10) {
            contact_profile_list {
                email
                place {
                    business_name
                }
            }
        }
    }
    '''

    # Mock PlaceModel.get to count calls
    with patch('ai_marketing_engine.models.place.PlaceModel.get') as mock_get:
        mock_get.return_value = MagicMock(place_uuid="test", business_name="Test")

        result = execute_query(query)

        # Should be 10 calls (N+1 issue)
        assert mock_get.call_count == 10, \
            f"Expected 10 individual place fetches (N+1 issue), got {mock_get.call_count}"


@pytest.mark.skip(reason="DataLoader not yet implemented")
def test_dataloader_eliminates_n_plus_one():
    """Once DataLoader is implemented, this should pass"""
    query = '''
    query {
        contact_profile_list(limit: 100) {
            contact_profile_list {
                place { business_name }
            }
        }
    }
    '''

    with patch('ai_marketing_engine.models.place.PlaceModel.batch_get') as mock_batch:
        mock_batch.return_value = [MagicMock(place_uuid=f"place-{i}") for i in range(100)]

        result = execute_query(query)

        # Should be 1 batch call instead of 100 individual calls
        assert mock_batch.call_count == 1
```

### Performance Comparison Table

| Implementation | 10 Records | 100 Records | 1000 Records | Notes |
|----------------|------------|-------------|--------------|-------|
| **Current (N+1)** | 41 queries | 401 queries | 4001 queries | Unacceptable for production |
| **With DataLoader** | 5 queries | 5 queries | 5 queries | 8-800x improvement |
| **With Cache** | 41 hits | 401 hits | 4001 hits | Fast but doesn't reduce load |
| **Eager Loading** | 5 queries | 5 queries | 5 queries | Similar to DataLoader |

### Conclusion

**N+1 query patterns are present and will cause significant performance issues** with list queries that include nested fields. The implementation is correct for single-record queries but **not optimized for batch operations**.

**Critical Action Required:**
- 🚨 **Do not use nested fields with large list queries in production** until DataLoader is implemented
- 📊 Implement query monitoring to detect performance issues
- 🎯 Prioritize DataLoader implementation (Phase 2)

---

## Questions & Answers

**Q: Will this break existing clients?**
A: Yes, clients querying `place`, `corporation_profile`, or `contact_profile` must update their queries to specify nested fields.

**Q: Can we maintain backward compatibility?**
A: Not easily with GraphQL. The type change from `JSON` to `PlaceType` is breaking. You could version the API, but that adds complexity.

**Q: What about N+1 query problems?**
A: **CONFIRMED: N+1 issues exist.** See "N+1 Query Pattern Analysis" section above for detailed analysis and mitigation strategies. DataLoader implementation is strongly recommended.

**Q: Do we need to change the database?**
A: No, all changes are in the application layer.

**Q: What if a resolver fails?**
A: GraphQL will return `null` for that field and include the error in the `errors` array.

**Q: Does the resolve_list_decorator need changes?**
A: No, the decorator is already compatible. It just calls the updated `get_*_type` functions.

---

## Next Steps

1. **Review this plan** with the team
2. **Create feature branch** and start Phase 1
3. **Run baseline tests** to capture current behavior
4. **Begin implementation** following phases sequentially
5. **Schedule deployment** after all tests pass

---

**Document Version:** 1.2
**Created:** 2025-11-22
**Updated:** 2025-11-23
**Author:** AI Assistant
**Status:** N+1 Analysis Complete - DataLoader Implementation Recommended
**Critical Findings:** N+1 query patterns identified in all nested resolvers - see "N+1 Query Pattern Analysis" section
