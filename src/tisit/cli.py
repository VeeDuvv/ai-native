# SPDX-License-Identifier: MIT
# Copyright (c) 2025 Vamsi Duvvuri

# Fifth Grade Explanation:
# This file lets us talk to our knowledge system using commands in the computer's command line.
# It's like having a special set of buttons that let us add, find, and connect pieces of
# knowledge without needing to write a lot of code each time.

# High School Explanation:
# This module implements a command-line interface for interacting with the TISIT knowledge
# graph. It provides commands for adding, querying, and managing entities and relationships,
# making the knowledge graph accessible through simple terminal commands.

import argparse
import sys
import os
import json
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
import textwrap
from datetime import datetime
import subprocess
import tempfile

from .entity import Entity
from .relationship import Relationship
from .knowledge_graph import KnowledgeGraph

class CLI:
    """Command-line interface for interacting with the TISIT knowledge graph.
    
    This class provides commands for adding, querying, and managing entities and
    relationships in the knowledge graph from the command line.
    """
    
    def __init__(self, storage_root: Optional[str] = None) -> None:
        """Initialize the CLI.
        
        Args:
            storage_root: Optional root directory for storing knowledge graph data.
                          If None, uses ~/.tisit or the TISIT_STORAGE_ROOT environment
                          variable if set.
        """
        if storage_root is None:
            storage_root = os.environ.get(
                'TISIT_STORAGE_ROOT',
                str(Path.home() / '.tisit')
            )
            
        self.storage_root = Path(storage_root)
        self.storage_root.mkdir(parents=True, exist_ok=True)
        
        self.knowledge_graph = KnowledgeGraph(str(self.storage_root))
    
    def run(self, args: Optional[List[str]] = None) -> None:
        """Run the CLI with the given arguments.
        
        Args:
            args: Command-line arguments (uses sys.argv if None)
        """
        parser = self._create_parser()
        parsed_args = parser.parse_args(args)
        
        if not hasattr(parsed_args, 'func'):
            parser.print_help()
            return
            
        parsed_args.func(parsed_args)
    
    def _create_parser(self) -> argparse.ArgumentParser:
        """Create the argument parser for the CLI.
        
        Returns:
            Configured argument parser
        """
        parser = argparse.ArgumentParser(
            description="TISIT Knowledge Graph CLI",
            formatter_class=argparse.RawDescriptionHelpFormatter
        )
        
        subparsers = parser.add_subparsers(title="commands", dest="command")
        
        # Add entity
        add_parser = subparsers.add_parser("add", help="Add a new entity")
        add_parser.add_argument("name", help="Name of the entity")
        add_parser.add_argument("--type", "-t", required=True, help="Type of entity")
        add_parser.add_argument("--desc", "-d", required=True, help="Short description")
        add_parser.add_argument("--detailed", help="Detailed description")
        add_parser.add_argument("--tags", nargs="+", help="Tags for the entity")
        add_parser.add_argument("--editor", "-e", action="store_true", help="Open editor for detailed description")
        add_parser.set_defaults(func=self._add_entity)
        
        # Find entities
        find_parser = subparsers.add_parser("find", help="Find entities")
        find_parser.add_argument("query", nargs="?", default="", help="Search query")
        find_parser.add_argument("--type", "-t", help="Filter by entity type")
        find_parser.add_argument("--tags", nargs="+", help="Filter by tags")
        find_parser.add_argument("--match-all", action="store_true", help="Require all tags to match")
        find_parser.add_argument("--full", "-f", action="store_true", help="Show full entity details")
        find_parser.set_defaults(func=self._find_entities)
        
        # View entity
        view_parser = subparsers.add_parser("view", help="View an entity")
        view_parser.add_argument("entity", help="Entity ID or name")
        view_parser.add_argument("--related", "-r", action="store_true", help="Show related entities")
        view_parser.add_argument("--depth", "-d", type=int, default=1, help="Depth for related entities")
        view_parser.add_argument("--format", choices=["text", "json"], default="text", help="Output format")
        view_parser.set_defaults(func=self._view_entity)
        
        # Update entity
        update_parser = subparsers.add_parser("update", help="Update an entity")
        update_parser.add_argument("entity", help="Entity ID or name")
        update_parser.add_argument("--name", help="New name")
        update_parser.add_argument("--desc", "-d", help="New short description")
        update_parser.add_argument("--detailed", help="New detailed description")
        update_parser.add_argument("--add-tags", nargs="+", help="Tags to add")
        update_parser.add_argument("--remove-tags", nargs="+", help="Tags to remove")
        update_parser.add_argument("--editor", "-e", action="store_true", help="Open editor for detailed description")
        update_parser.set_defaults(func=self._update_entity)
        
        # Delete entity
        delete_parser = subparsers.add_parser("delete", help="Delete an entity")
        delete_parser.add_argument("entity", help="Entity ID or name")
        delete_parser.add_argument("--force", "-f", action="store_true", help="Skip confirmation")
        delete_parser.set_defaults(func=self._delete_entity)
        
        # Link entities
        link_parser = subparsers.add_parser("link", help="Create a relationship between entities")
        link_parser.add_argument("source", help="Source entity ID or name")
        link_parser.add_argument("target", help="Target entity ID or name")
        link_parser.add_argument("--type", "-t", required=True, help="Type of relationship")
        link_parser.add_argument("--desc", "-d", help="Relationship description")
        link_parser.add_argument("--bidirectional", "-b", action="store_true", help="Bidirectional relationship")
        link_parser.set_defaults(func=self._link_entities)
        
        # View relationships
        relations_parser = subparsers.add_parser("relations", help="View entity relationships")
        relations_parser.add_argument("entity", help="Entity ID or name")
        relations_parser.add_argument("--direction", "-d", choices=["outgoing", "incoming", "both"], default="both", help="Relationship direction")
        relations_parser.set_defaults(func=self._view_relationships)
        
        # Find connections
        connect_parser = subparsers.add_parser("connect", help="Find connections between entities")
        connect_parser.add_argument("source", help="Source entity ID or name")
        connect_parser.add_argument("target", help="Target entity ID or name")
        connect_parser.add_argument("--max-depth", "-d", type=int, default=3, help="Maximum path length")
        connect_parser.set_defaults(func=self._find_connections)
        
        # Statistics
        stats_parser = subparsers.add_parser("stats", help="Show knowledge graph statistics")
        stats_parser.set_defaults(func=self._show_stats)
        
        # Visualize
        viz_parser = subparsers.add_parser("visualize", help="Visualize the knowledge graph")
        viz_parser.add_argument("--output", "-o", default="knowledge_graph.png", help="Output file path")
        viz_parser.add_argument("--entities", nargs="+", help="Specific entities to include")
        viz_parser.add_argument("--no-labels", action="store_true", help="Hide labels")
        viz_parser.add_argument("--layout", choices=["spring", "circular", "random"], default="spring", help="Layout algorithm")
        viz_parser.set_defaults(func=self._visualize)
        
        return parser
    
    def _resolve_entity(self, entity_ref: str) -> Optional[Entity]:
        """Resolve an entity reference (ID or name) to an Entity.
        
        Args:
            entity_ref: Entity ID or name
            
        Returns:
            Entity if found, None otherwise
        """
        # Try as ID first
        entity = self.knowledge_graph.get_entity(entity_ref)
        if entity:
            return entity
            
        # Try as name
        return self.knowledge_graph.entity_storage.find_by_name(entity_ref)
    
    def _print_entity_summary(self, entity: Entity) -> None:
        """Print a summary of an entity.
        
        Args:
            entity: The entity to summarize
        """
        print(f"{entity.name} ({entity.type}) [{entity.id}]")
        print(f"  {entity.short_description}")
        if entity.tags:
            print(f"  Tags: {', '.join(entity.tags)}")
            
    def _print_entity_full(self, entity: Entity) -> None:
        """Print full details of an entity.
        
        Args:
            entity: The entity to display
        """
        print(f"ID: {entity.id}")
        print(f"Name: {entity.name}")
        print(f"Type: {entity.type}")
        print(f"Created: {entity.first_encountered}")
        print(f"Updated: {entity.last_updated}")
        print(f"Tags: {', '.join(entity.tags) if entity.tags else 'None'}")
        print(f"Short Description: {entity.short_description}")
        
        if entity.detailed_description:
            print("\nDetailed Description:")
            print(textwrap.fill(entity.detailed_description, width=80, initial_indent="  ", subsequent_indent="  "))
            
        if entity.links:
            print("\nLinks:")
            for link in entity.links:
                linked_entity = self.knowledge_graph.get_entity(link["target_id"])
                name = linked_entity.name if linked_entity else link["target_id"]
                print(f"  {link['relation_type']} → {name}")
                
        if entity.references:
            print("\nReferences:")
            for ref in entity.references:
                print(f"  {ref['type']}: {ref['location']}")
                if ref['context']:
                    print(f"    {ref['context']}")
                    
        if entity.metadata:
            print("\nMetadata:")
            for key, value in entity.metadata.items():
                print(f"  {key}: {value}")
    
    def _add_entity(self, args: argparse.Namespace) -> None:
        """Handle the 'add' command.
        
        Args:
            args: Parsed command-line arguments
        """
        detailed_desc = args.detailed or ""
        
        if args.editor:
            # Open an editor for the detailed description
            with tempfile.NamedTemporaryFile(suffix=".txt", mode="w+", delete=False) as temp:
                if detailed_desc:
                    temp.write(detailed_desc)
                temp_path = temp.name
                
            editor = os.environ.get("EDITOR", "nano")
            subprocess.call([editor, temp_path])
            
            with open(temp_path, "r") as temp:
                detailed_desc = temp.read().strip()
                
            os.unlink(temp_path)
            
        # Create and add the entity
        entity = Entity(
            name=args.name,
            entity_type=args.type,
            short_description=args.desc,
            detailed_description=detailed_desc,
            tags=args.tags
        )
        
        entity_id = self.knowledge_graph.add_entity(entity)
        print(f"Added entity: {args.name} ({args.type}) [{entity_id}]")
    
    def _find_entities(self, args: argparse.Namespace) -> None:
        """Handle the 'find' command.
        
        Args:
            args: Parsed command-line arguments
        """
        entities = []
        
        # Apply filters in order of specificity
        if args.type:
            entities = self.knowledge_graph.find_entities_by_type(args.type)
            
            if args.tags:
                # Further filter by tags
                entities = [e for e in entities if all(tag in e.tags for tag in args.tags)]
                
            if args.query:
                # Further filter by query
                query_lower = args.query.lower()
                entities = [e for e in entities if
                          query_lower in e.name.lower() or
                          query_lower in e.short_description.lower() or
                          (e.detailed_description and query_lower in e.detailed_description.lower())]
        elif args.tags:
            entities = self.knowledge_graph.find_entities_by_tags(args.tags, args.match_all)
            
            if args.query:
                # Further filter by query
                query_lower = args.query.lower()
                entities = [e for e in entities if
                          query_lower in e.name.lower() or
                          query_lower in e.short_description.lower() or
                          (e.detailed_description and query_lower in e.detailed_description.lower())]
        else:
            # Just search by query
            entities = self.knowledge_graph.find_entities(args.query)
            
        if not entities:
            print("No matching entities found.")
            return
            
        print(f"Found {len(entities)} matching entities:\n")
        
        for entity in entities:
            if args.full:
                self._print_entity_full(entity)
                print("\n" + "-" * 40 + "\n")
            else:
                self._print_entity_summary(entity)
    
    def _view_entity(self, args: argparse.Namespace) -> None:
        """Handle the 'view' command.
        
        Args:
            args: Parsed command-line arguments
        """
        entity = self._resolve_entity(args.entity)
        
        if not entity:
            print(f"Entity not found: {args.entity}")
            return
            
        if args.format == "json":
            # JSON output
            result = entity.to_dict()
            
            if args.related:
                related = self.knowledge_graph.get_related_entities(entity.id, max_depth=args.depth)
                result["related"] = {
                    rel_type: [e.to_dict() for e in entities]
                    for rel_type, entities in related.items()
                }
                
            print(json.dumps(result, indent=2))
        else:
            # Text output
            self._print_entity_full(entity)
            
            if args.related:
                related = self.knowledge_graph.get_related_entities(entity.id, max_depth=args.depth)
                
                if related:
                    print("\nRelated Entities:")
                    for rel_type, entities in related.items():
                        print(f"  {rel_type}:")
                        for related_entity in entities:
                            print(f"    {related_entity.name} ({related_entity.type}) [{related_entity.id}]")
    
    def _update_entity(self, args: argparse.Namespace) -> None:
        """Handle the 'update' command.
        
        Args:
            args: Parsed command-line arguments
        """
        entity = self._resolve_entity(args.entity)
        
        if not entity:
            print(f"Entity not found: {args.entity}")
            return
            
        # Update fields if provided
        if args.name:
            entity.name = args.name
            
        if args.desc:
            entity.short_description = args.desc
            
        detailed_desc = args.detailed
        
        if args.editor:
            # Open an editor for the detailed description
            with tempfile.NamedTemporaryFile(suffix=".txt", mode="w+", delete=False) as temp:
                temp.write(entity.detailed_description)
                temp_path = temp.name
                
            editor = os.environ.get("EDITOR", "nano")
            subprocess.call([editor, temp_path])
            
            with open(temp_path, "r") as temp:
                detailed_desc = temp.read().strip()
                
            os.unlink(temp_path)
            
        if detailed_desc is not None:
            entity.detailed_description = detailed_desc
            
        # Add tags
        if args.add_tags:
            for tag in args.add_tags:
                entity.add_tag(tag)
                
        # Remove tags
        if args.remove_tags:
            for tag in args.remove_tags:
                entity.remove_tag(tag)
                
        # Save the updated entity
        self.knowledge_graph.update_entity(entity)
        print(f"Updated entity: {entity.name} ({entity.type}) [{entity.id}]")
    
    def _delete_entity(self, args: argparse.Namespace) -> None:
        """Handle the 'delete' command.
        
        Args:
            args: Parsed command-line arguments
        """
        entity = self._resolve_entity(args.entity)
        
        if not entity:
            print(f"Entity not found: {args.entity}")
            return
            
        if not args.force:
            # Confirm deletion
            response = input(f"Delete entity '{entity.name}' ({entity.id})? [y/N] ")
            if response.lower() not in ["y", "yes"]:
                print("Deletion cancelled.")
                return
                
        # Delete the entity
        self.knowledge_graph.delete_entity(entity.id)
        print(f"Deleted entity: {entity.name} ({entity.type}) [{entity.id}]")
    
    def _link_entities(self, args: argparse.Namespace) -> None:
        """Handle the 'link' command.
        
        Args:
            args: Parsed command-line arguments
        """
        source_entity = self._resolve_entity(args.source)
        target_entity = self._resolve_entity(args.target)
        
        if not source_entity:
            print(f"Source entity not found: {args.source}")
            return
            
        if not target_entity:
            print(f"Target entity not found: {args.target}")
            return
            
        # Create the relationship
        rel_id = self.knowledge_graph.add_relationship(
            source_id=source_entity.id,
            target_id=target_entity.id,
            relation_type=args.type,
            description=args.desc,
            bidirectional=args.bidirectional
        )
        
        if rel_id:
            print(f"Created relationship: {source_entity.name} -{args.type}-> {target_entity.name}")
        else:
            print("Failed to create relationship.")
    
    def _view_relationships(self, args: argparse.Namespace) -> None:
        """Handle the 'relations' command.
        
        Args:
            args: Parsed command-line arguments
        """
        entity = self._resolve_entity(args.entity)
        
        if not entity:
            print(f"Entity not found: {args.entity}")
            return
            
        relationships = self.knowledge_graph.get_entity_relationships(entity.id, args.direction)
        
        if not relationships:
            print(f"No {args.direction} relationships found for {entity.name}.")
            return
            
        print(f"{args.direction.capitalize()} relationships for {entity.name}:")
        
        for rel in relationships:
            source = self.knowledge_graph.get_entity(rel.source_id)
            target = self.knowledge_graph.get_entity(rel.target_id)
            
            source_name = source.name if source else rel.source_id
            target_name = target.name if target else rel.target_id
            
            print(f"  {source_name} -{rel.type}-> {target_name}")
            if rel.description:
                print(f"    Description: {rel.description}")
                
            if rel.properties:
                print(f"    Properties: {json.dumps(rel.properties)}")
                
            if rel.bidirectional:
                print(f"    Bidirectional: Yes")
    
    def _find_connections(self, args: argparse.Namespace) -> None:
        """Handle the 'connect' command.
        
        Args:
            args: Parsed command-line arguments
        """
        source_entity = self._resolve_entity(args.source)
        target_entity = self._resolve_entity(args.target)
        
        if not source_entity:
            print(f"Source entity not found: {args.source}")
            return
            
        if not target_entity:
            print(f"Target entity not found: {args.target}")
            return
            
        paths = self.knowledge_graph.find_connections(
            source_entity.id,
            target_entity.id,
            args.max_depth
        )
        
        if not paths:
            print(f"No connection found between {source_entity.name} and {target_entity.name} within {args.max_depth} steps.")
            return
            
        print(f"Found {len(paths)} connection{'' if len(paths) == 1 else 's'} between {source_entity.name} and {target_entity.name}:")
        
        for i, path in enumerate(paths):
            print(f"\nPath {i+1}:")
            for source_id, rel_type, target_id in path:
                source = self.knowledge_graph.get_entity(source_id)
                target = self.knowledge_graph.get_entity(target_id)
                
                source_name = source.name if source else source_id
                target_name = target.name if target else target_id
                
                print(f"  {source_name} -{rel_type}-> {target_name}")
    
    def _show_stats(self, args: argparse.Namespace) -> None:
        """Handle the 'stats' command.
        
        Args:
            args: Parsed command-line arguments
        """
        stats = self.knowledge_graph.get_stats()
        
        print("Knowledge Graph Statistics")
        print("-" * 25)
        print(f"Entities: {stats['num_entities']}")
        print(f"Relationships: {stats['num_relationships']}")
        print(f"Graph Density: {stats['density']:.4f}")
        
        if stats['entity_types']:
            print("\nEntity Types:")
            for entity_type, count in sorted(stats['entity_types'].items(), key=lambda x: x[1], reverse=True):
                print(f"  {entity_type}: {count}")
                
        if stats['relationship_types']:
            print("\nRelationship Types:")
            for rel_type, count in sorted(stats['relationship_types'].items(), key=lambda x: x[1], reverse=True):
                print(f"  {rel_type}: {count}")
                
        if stats['top_connected_entities']:
            print("\nMost Connected Entities:")
            for entity_info in stats['top_connected_entities']:
                print(f"  {entity_info['name']} ({entity_info['type']}): {entity_info['connections']} connections")
    
    def _visualize(self, args: argparse.Namespace) -> None:
        """Handle the 'visualize' command.
        
        Args:
            args: Parsed command-line arguments
        """
        entity_ids = None
        
        if args.entities:
            # Resolve entity references to IDs
            entity_ids = []
            for entity_ref in args.entities:
                entity = self._resolve_entity(entity_ref)
                if entity:
                    entity_ids.append(entity.id)
                else:
                    print(f"Warning: Entity not found: {entity_ref}")
                    
            if not entity_ids:
                print("No valid entities specified for visualization.")
                return
                
        try:
            self.knowledge_graph.export_to_visualization(
                output_file=args.output,
                entity_ids=entity_ids,
                include_labels=not args.no_labels,
                layout=args.layout
            )
            print(f"Visualization saved to {args.output}")
        except Exception as e:
            print(f"Error creating visualization: {e}")


def main() -> None:
    """Main entry point for the CLI."""
    cli = CLI()
    cli.run()


if __name__ == "__main__":
    main()