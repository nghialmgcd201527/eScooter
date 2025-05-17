# leanix_api/__init__.py
from .application import get_application_factsheet
from .it_component import create_it_component_with_relation

# Rename the function for external use
create_it_component = create_it_component_with_relation