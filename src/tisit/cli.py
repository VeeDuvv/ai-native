# SPDX-License-Identifier: MIT
# Copyright (c) 2025 Vamsi Duvvuri

# Fifth Grade Explanation:
# This file makes a tool that lets people use the knowledge brain from their computer.
# It's like a special remote control for our knowledge library.

# High School Explanation:
# This module implements a command-line interface for the TISIT knowledge graph system.
# It provides commands for viewing, adding, updating, and querying knowledge entities
# and their relationships through a user-friendly terminal interface.

import os
import sys
import json
import argparse
import logging
from typing import Dict, List, Optional, Any
from pathlib import Path

from .entity import Entity
from .relationship import Relationship
from .knowledge_graph import KnowledgeGraph

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

DEFAULT_DATA_DIR = os.path.expanduser("~/.tisit")


def setup_parser() -> argparse.ArgumentParser:
    """Set up the command-line argument parser."""
    parser = argparse.ArgumentParser(
        description="TISIT - This Is What It Is - Knowledge Graph CLI",
        epilog="Use 'tisit COMMAND --help' for more information about a command."
    )
    
    parser.add_argument('--data-dir', type=str, default=DEFAULT_DATA_DIR,
                      help="Directory for storing TISIT data")
    
    subparsers = parser.add_subparsers(dest='command', help='Command to execute')
    
    # Add entity command
    add_parser = subparsers.add_parser('add', help='Add a new entity')
    add_parser.add_argument('type', type=str, help='Entity type')
    add_parser.add_argument('name', type=str, help='Entity name')
    add_parser.add_argument('--short', '-s', type=str, help='Short description')
    add_parser.add_argument('--detailed', '-d', type=str, help='Detailed description')
    add_parser.add_argument('--tags', '-t', type=str, nargs='+', help='Tags')
    add_parser.add_argument('--metadata', '-m', type=str, help='Metadata as JSON string')
    
    # View entity command
    view_parser = subparsers.add_parser('view', help='View an entity')
    view_parser.add_argument('name', type=str, help='Entity name or ID')
    view_parser.add_argument('--related', '-r', action='store_true', 
                           help='Show related entities')
    view_parser.add_argument('--depth', type=int, default=1,
                           help='Depth of related entities to show')
    
    # List entities command
    list_parser = subparsers.add_parser('list', help='List entities')
    list_parser.add_argument('--type', '-t', type=str, help='Filter by entity type')
    list_parser.add_argument('--tag', type=str, help='Filter by tag')
    list_parser.add_argument('--limit', '-l', type=int, default=20,
                           help='Maximum number of entities to show')
    
    # Link entities command
    link_parser = subparsers.add_parser('link', help='Create a relationship between entities')
    link_parser.add_argument('source', type=str, help='Source entity name')
    link_parser.add_argument('target', type=str, help='Target entity name')
    link_parser.add_argument('relation', type=str, help='Relationship type')
    link_parser.add_argument('--description', '-d', type=str, 
                           help='Relationship description')
    link_parser.add_argument('--weight', '-w', type=float, default=1.0,
                           help='Relationship weight (0.0 to 1.0)')
    
    # Search command
    search_parser = subparsers.add_parser('search', help='Search for entities')
    search_parser.add_argument('query', type=str, help='Search query')
    search_parser.add_argument('--type', '-t', type=str, help='Filter by entity type')
    search_parser.add_argument('--tags', type=str, nargs='+', help='Filter by tags')
    
    # Update entity command
    update_parser = subparsers.add_parser('update', help='Update an entity')
    update_parser.add_argument('name', type=str, help='Entity name or ID')
    update_parser.add_argument('--short', '-s', type=str, help='New short description')
    update_parser.add_argument('--detailed', '-d', type=str, help='New detailed description')
    update_parser.add_argument('--add-tags', type=str, nargs='+', help='Tags to add')
    update_parser.add_argument('--remove-tags', type=str, nargs='+', help='Tags to remove')
    update_parser.add_argument('--metadata', '-m', type=str, help='Metadata as JSON string to merge')
    
    # Delete entity command
    delete_parser = subparsers.add_parser('delete', help='Delete an entity')
    delete_parser.add_argument('name', type=str, help='Entity name or ID')
    delete_parser.add_argument('--force', '-f', action='store_true',
                             help='Force deletion without confirmation')
    
    # Visualize command
    viz_parser = subparsers.add_parser('visualize', help='Visualize the knowledge graph')
    viz_parser.add_argument('--entities', '-e', type=str, nargs='+',
                          help='Entity names to include (defaults to all)')
    viz_parser.add_argument('--output', '-o', type=str, 
                          help='Output file path (defaults to display on screen)')
    viz_parser.add_argument('--max-nodes', type=int, default=50,
                          help='Maximum number of nodes to include')
    
    # Import command
    import_parser = subparsers.add_parser('import', help='Import entities from JSON file')
    import_parser.add_argument('file', type=str, help='JSON file path')
    
    # Export command
    export_parser = subparsers.add_parser('export', help='Export entities to JSON file')
    export_parser.add_argument('file', type=str, help='Output JSON file path')
    export_parser.add_argument('--type', '-t', type=str, help='Export only entities of this type')
    export_parser.add_argument('--tag', type=str, help='Export only entities with this tag')
    
    # Stats command
    subparsers.add_parser('stats', help='Show statistics about the knowledge graph')
    
    return parser


def find_entity_by_name_or_id(kg: KnowledgeGraph, name_or_id: str) -> Optional[Entity]:
    """Find an entity by its name or ID."""
    # Try direct ID lookup first
    entity = kg.get_entity(name_or_id)
    if entity:
        return entity
    
    # Search by name
    entities = kg.find_entities(query=name_or_id)
    
    # Return entity with exact name match if found
    for entity in entities:
        if entity.name.lower() == name_or_id.lower():
            return entity
    
    # Otherwise return first match
    return entities[0] if entities else None


def command_add(args: argparse.Namespace, kg: KnowledgeGraph) -> None:
    """Handle the 'add' command."""
    # Parse metadata if provided
    metadata = {}
    if args.metadata:
        try:
            metadata = json.loads(args.metadata)
        except json.JSONDecodeError:
            logger.error("Invalid JSON in metadata")
            return
    
    # Create entity
    entity = Entity(
        name=args.name,
        entity_type=args.type,
        short_description=args.short or "",
        detailed_description=args.detailed or "",
        tags=args.tags or [],
        metadata=metadata
    )
    
    # Add to knowledge graph
    entity_id = kg.add_entity(entity)
    
    print(f"Added entity: {args.name} (ID: {entity_id})")
    print(f"Type: {args.type}")
    if args.short:
        print(f"Description: {args.short}")


def command_view(args: argparse.Namespace, kg: KnowledgeGraph) -> None:
    """Handle the 'view' command."""
    entity = find_entity_by_name_or_id(kg, args.name)
    
    if not entity:
        logger.error(f"Entity not found: {args.name}")
        return
    
    # Print entity details
    print(f"Name: {entity.name}")
    print(f"ID: {entity.id}")
    print(f"Type: {entity.entity_type}")
    print(f"Created: {entity.created_at}")
    print(f"Updated: {entity.updated_at}")
    
    if entity.short_description:
        print(f"\nShort description: {entity.short_description}")
    
    if entity.detailed_description:
        print(f"\nDetailed description:\n{entity.detailed_description}")
    
    if entity.tags:
        print(f"\nTags: {', '.join(entity.tags)}")
    
    if entity.metadata:
        print("\nMetadata:")
        for key, value in entity.metadata.items():
            print(f"  {key}: {value}")
    
    # Show related entities if requested
    if args.related:
        related = kg.get_related_entities(entity.id, depth=args.depth)
        
        if related:
            print("\nRelated entities:")
            for rel in related:
                rel_entity = rel["entity"]
                rel_type = rel["relationship"]
                direction = rel["direction"]
                
                if direction == "outgoing":
                    print(f"  {entity.name} --[{rel_type}]--> {rel_entity.name}")
                else:
                    print(f"  {rel_entity.name} --[{rel_type}]--> {entity.name}")


def command_list(args: argparse.Namespace, kg: KnowledgeGraph) -> None:
    """Handle the 'list' command."""
    # Get entities based on filters
    if args.type:
        entities = kg.storage.get_entities_by_type(args.type)
    elif args.tag:
        entities = kg.storage.get_entities_by_tag(args.tag)
    else:
        # Get all entities
        entities = [kg.get_entity(eid) for eid in kg.storage.list_entities()]
        entities = [e for e in entities if e is not None]
    
    # Limit results
    entities = entities[:args.limit]
    
    if not entities:
        print("No entities found")
        return
    
    print(f"Found {len(entities)} entities:")
    for entity in entities:
        print(f"- {entity.name} ({entity.entity_type}): {entity.short_description}")


def command_link(args: argparse.Namespace, kg: KnowledgeGraph) -> None:
    """Handle the 'link' command."""
    source_entity = find_entity_by_name_or_id(kg, args.source)
    if not source_entity:
        logger.error(f"Source entity not found: {args.source}")
        return
    
    target_entity = find_entity_by_name_or_id(kg, args.target)
    if not target_entity:
        logger.error(f"Target entity not found: {args.target}")
        return
    
    # Create relationship
    rel_id = kg.add_relationship(
        source_id=source_entity.id,
        target_id=target_entity.id,
        relation_type=args.relation,
        description=args.description or "",
        weight=args.weight
    )
    
    print(f"Added relationship: {source_entity.name} --[{args.relation}]--> {target_entity.name}")
    print(f"Relationship ID: {rel_id}")


def command_search(args: argparse.Namespace, kg: KnowledgeGraph) -> None:
    """Handle the 'search' command."""
    entities = kg.find_entities(
        query=args.query,
        entity_type=args.type,
        tags=args.tags
    )
    
    if not entities:
        print("No matching entities found")
        return
    
    print(f"Found {len(entities)} matches:")
    for entity in entities:
        print(f"- {entity.name} ({entity.entity_type}): {entity.short_description}")


def command_update(args: argparse.Namespace, kg: KnowledgeGraph) -> None:
    """Handle the 'update' command."""
    entity = find_entity_by_name_or_id(kg, args.name)
    
    if not entity:
        logger.error(f"Entity not found: {args.name}")
        return
    
    # Update descriptions if provided
    if args.short is not None or args.detailed is not None:
        entity.update_description(short=args.short, detailed=args.detailed)
    
    # Add tags
    if args.add_tags:
        for tag in args.add_tags:
            entity.add_tag(tag)
    
    # Remove tags
    if args.remove_tags:
        for tag in args.remove_tags:
            entity.remove_tag(tag)
    
    # Update metadata
    if args.metadata:
        try:
            new_metadata = json.loads(args.metadata)
            for key, value in new_metadata.items():
                entity.add_metadata(key, value)
        except json.JSONDecodeError:
            logger.error("Invalid JSON in metadata")
            return
    
    # Save entity
    kg.storage.save_entity(entity)
    
    print(f"Updated entity: {entity.name}")


def command_delete(args: argparse.Namespace, kg: KnowledgeGraph) -> None:
    """Handle the 'delete' command."""
    entity = find_entity_by_name_or_id(kg, args.name)
    
    if not entity:
        logger.error(f"Entity not found: {args.name}")
        return
    
    # Ask for confirmation unless --force is used
    if not args.force:
        confirm = input(f"Are you sure you want to delete '{entity.name}'? [y/N] ")
        if confirm.lower() != 'y':
            print("Deletion cancelled")
            return
    
    # Delete entity
    success = kg.delete_entity(entity.id)
    
    if success:
        print(f"Deleted entity: {entity.name}")
    else:
        logger.error(f"Failed to delete entity: {entity.name}")


def command_visualize(args: argparse.Namespace, kg: KnowledgeGraph) -> None:
    """Handle the 'visualize' command."""
    # Get entity IDs if specified
    entity_ids = []
    if args.entities:
        for name in args.entities:
            entity = find_entity_by_name_or_id(kg, name)
            if entity:
                entity_ids.append(entity.id)
            else:
                logger.warning(f"Entity not found: {name}")
    
    # Generate visualization
    kg.visualize(
        entity_ids=entity_ids if entity_ids else None,
        output_path=args.output,
        max_nodes=args.max_nodes
    )


def command_import(args: argparse.Namespace, kg: KnowledgeGraph) -> None:
    """Handle the 'import' command."""
    try:
        with open(args.file, 'r') as f:
            data = json.load(f)
        
        if not isinstance(data, list):
            logger.error("Import file must contain a list of entities")
            return
        
        imported_count = 0
        for entity_data in data:
            try:
                entity = Entity.from_dict(entity_data)
                kg.add_entity(entity)
                imported_count += 1
            except (ValueError, KeyError) as e:
                logger.warning(f"Failed to import entity: {str(e)}")
        
        print(f"Imported {imported_count} entities from {args.file}")
    
    except json.JSONDecodeError:
        logger.error("Invalid JSON file")
    except FileNotFoundError:
        logger.error(f"File not found: {args.file}")


def command_export(args: argparse.Namespace, kg: KnowledgeGraph) -> None:
    """Handle the 'export' command."""
    # Get entities based on filters
    if args.type:
        entities = kg.storage.get_entities_by_type(args.type)
    elif args.tag:
        entities = kg.storage.get_entities_by_tag(args.tag)
    else:
        # Get all entities
        entities = [kg.get_entity(eid) for eid in kg.storage.list_entities()]
        entities = [e for e in entities if e is not None]
    
    # Export to JSON
    export_data = [entity.to_dict() for entity in entities]
    
    try:
        with open(args.file, 'w') as f:
            json.dump(export_data, f, indent=2)
        
        print(f"Exported {len(export_data)} entities to {args.file}")
    
    except OSError as e:
        logger.error(f"Failed to write export file: {str(e)}")


def command_stats(args: argparse.Namespace, kg: KnowledgeGraph) -> None:
    """Handle the 'stats' command."""
    stats = kg.get_statistics()
    
    print("Knowledge Graph Statistics:")
    print(f"Entities: {stats['entity_count']}")
    print(f"Relationships: {stats['relationship_count']}")
    
    if stats['entity_types']:
        print("\nEntity types:")
        for entity_type, count in stats['entity_types'].items():
            print(f"  {entity_type}: {count}")
    
    if stats['relationship_types']:
        print("\nRelationship types:")
        for rel_type, count in stats['relationship_types'].items():
            print(f"  {rel_type}: {count}")


def main():
    """Main entry point for the CLI."""
    parser = setup_parser()
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # Ensure data directory exists
    data_dir = Path(args.data_dir)
    data_dir.mkdir(parents=True, exist_ok=True)
    
    # Initialize knowledge graph
    kg = KnowledgeGraph(str(data_dir))
    
    # Handle command
    command_handlers = {
        'add': command_add,
        'view': command_view,
        'list': command_list,
        'link': command_link,
        'search': command_search,
        'update': command_update,
        'delete': command_delete,
        'visualize': command_visualize,
        'import': command_import,
        'export': command_export,
        'stats': command_stats
    }
    
    if args.command in command_handlers:
        command_handlers[args.command](args, kg)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()