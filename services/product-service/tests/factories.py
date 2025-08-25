"""Test data factories using Factory Boy."""
import factory
import uuid
from faker import Faker

from app.models.product import Product, ProductCategory, ProductTag, ProductType, ProductUnit
from app.extensions import db

fake = Faker()


class ProductCategoryFactory(factory.alchemy.SQLAlchemyModelFactory):
    """Factory for ProductCategory model."""
    
    class Meta:
        model = ProductCategory
        sqlalchemy_session = db.session
        sqlalchemy_session_persistence = "commit"
    
    name = factory.Sequence(lambda n: f"Category {n}")
    description = factory.Faker('text', max_nb_chars=200)
    color = factory.Faker('color')


class ProductTagFactory(factory.alchemy.SQLAlchemyModelFactory):
    """Factory for ProductTag model."""
    
    class Meta:
        model = ProductTag
        sqlalchemy_session = db.session
        sqlalchemy_session_persistence = "commit"
    
    name = factory.Sequence(lambda n: f"tag-{n}")


class ProductFactory(factory.alchemy.SQLAlchemyModelFactory):
    """Factory for Product model."""
    
    class Meta:
        model = Product
        sqlalchemy_session = db.session
        sqlalchemy_session_persistence = "commit"
    
    name = factory.Sequence(lambda n: f"Product {n}")
    type = factory.Faker('random_element', elements=[t for t in ProductType])
    unit = factory.Faker('random_element', elements=[u for u in ProductUnit])
    description = factory.Faker('text', max_nb_chars=500)
    created_by = factory.LazyFunction(uuid.uuid4)
    updated_by = factory.LazyFunction(uuid.uuid4)
    
    @factory.post_generation
    def categories(self, create, extracted, **kwargs):
        """Add categories to the product."""
        if not create:
            return
        
        if extracted:
            for category in extracted:
                self.categories.append(category)
    
    @factory.post_generation
    def tags(self, create, extracted, **kwargs):
        """Add tags to the product."""
        if not create:
            return
        
        if extracted:
            for tag in extracted:
                self.tags.append(tag)


class StandardProductFactory(ProductFactory):
    """Factory for standard products."""
    type = ProductType.STANDARD
    unit = ProductUnit.PIECE


class KitProductFactory(ProductFactory):
    """Factory for kit products."""
    type = ProductType.KIT
    unit = ProductUnit.GRAM


class SemiProductFactory(ProductFactory):
    """Factory for semi-products."""
    type = ProductType.SEMI_PRODUCT