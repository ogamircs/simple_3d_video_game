"""
Combat System
Centralized damage calculation and application.
"""
from ursina import distance, Vec3
from config import (
    DAMAGE_FALLOFF_START, DAMAGE_FALLOFF_END,
    DAMAGE_MINIMUM_MULTIPLIER, HEADSHOT_MULTIPLIER
)


class CombatSystem:
    """Static class for handling combat mechanics."""

    @staticmethod
    def apply_damage(target, damage, source=None, hit_position=None):
        """
        Apply damage to a target with falloff and modifiers.

        Args:
            target: Entity to damage (must have take_damage method)
            damage: Base damage amount
            source: Entity that caused the damage
            hit_position: World position of the hit (for headshots)
        """
        if not hasattr(target, 'take_damage'):
            return 0

        final_damage = damage

        # Distance-based damage falloff
        if source and hasattr(source, 'position'):
            final_damage = CombatSystem.calculate_falloff(
                final_damage, source.position, target.position
            )

        # Headshot bonus
        if hit_position and hasattr(target, 'world_position'):
            final_damage = CombatSystem.calculate_headshot(
                final_damage, hit_position, target
            )

        # Apply the damage
        final_damage = int(final_damage)
        target.take_damage(final_damage, source=source)

        return final_damage

    @staticmethod
    def calculate_falloff(damage, source_pos, target_pos):
        """
        Calculate damage falloff based on distance.

        Args:
            damage: Base damage
            source_pos: Position of damage source
            target_pos: Position of target

        Returns:
            Adjusted damage value
        """
        dist = distance(source_pos, target_pos)

        if dist <= DAMAGE_FALLOFF_START:
            return damage

        if dist >= DAMAGE_FALLOFF_END:
            return damage * DAMAGE_MINIMUM_MULTIPLIER

        # Linear falloff between start and end
        falloff_range = DAMAGE_FALLOFF_END - DAMAGE_FALLOFF_START
        falloff_progress = (dist - DAMAGE_FALLOFF_START) / falloff_range
        multiplier = 1 - (falloff_progress * (1 - DAMAGE_MINIMUM_MULTIPLIER))

        return damage * multiplier

    @staticmethod
    def calculate_headshot(damage, hit_position, target):
        """
        Apply headshot multiplier if hit is in upper portion of target.

        Args:
            damage: Current damage value
            hit_position: World position of hit
            target: Target entity

        Returns:
            Adjusted damage value
        """
        # Get target's height
        target_height = getattr(target, 'scale_y', 1)
        if hasattr(target, 'scale') and hasattr(target.scale, 'y'):
            target_height = target.scale.y

        # Calculate hit height relative to target
        hit_height = hit_position.y - target.world_position.y

        # Upper 30% is considered headshot zone
        headshot_threshold = target_height * 0.7

        if hit_height > headshot_threshold:
            return damage * HEADSHOT_MULTIPLIER

        return damage

    @staticmethod
    def is_line_of_sight(from_entity, to_entity, ignore_list=None):
        """
        Check if there's a clear line of sight between two entities.

        Args:
            from_entity: Starting entity
            to_entity: Target entity
            ignore_list: List of entities to ignore in raycast

        Returns:
            True if clear line of sight exists
        """
        from ursina import raycast, Vec3

        if ignore_list is None:
            ignore_list = []

        # Add both entities to ignore list
        ignore_list = ignore_list + [from_entity, to_entity]

        # Calculate direction
        from_pos = from_entity.position
        if hasattr(from_entity, 'world_position'):
            from_pos = from_entity.world_position

        to_pos = to_entity.position
        if hasattr(to_entity, 'world_position'):
            to_pos = to_entity.world_position

        # Offset to eye level
        from_pos = from_pos + Vec3(0, 1, 0)
        to_pos = to_pos + Vec3(0, 1, 0)

        direction = (to_pos - from_pos).normalized()
        dist = (to_pos - from_pos).length()

        # Raycast
        hit_info = raycast(
            origin=from_pos,
            direction=direction,
            distance=dist,
            ignore=ignore_list
        )

        # If we didn't hit anything, we have line of sight
        return not hit_info.hit
