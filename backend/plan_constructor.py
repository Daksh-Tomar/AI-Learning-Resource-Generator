def construct_plan(ranked_resources: list, available_hours_per_week: float, num_weeks: int = 8, start_difficulty: str = "beginner"):
    """
    Constructs a week-by-week learning plan from ranked resources.
    """
    plan = []
    
    # Sort resources by difficulty logically
    difficulty_order = {"beginner": 1, "intermediate": 2, "advanced": 3}
    
    # Filter and sort resources based on the starting difficulty
    # If starting at beginner, we want to progress to advanced
    # We will just roughly sort by difficulty and then by similarity score
    filtered_resources = [r for r in ranked_resources if difficulty_order.get(r['resource'].difficulty_level, 1) >= difficulty_order.get(start_difficulty, 1)]
    
    filtered_resources.sort(key=lambda x: (
        difficulty_order.get(x['resource'].difficulty_level, 1),
        -x['similarity_score'] # Highest similarity first
    ))

    used_resource_ids = set()
    current_week = 1
    
    while current_week <= num_weeks and len(used_resource_ids) < len(filtered_resources):
        week_hours = 0.0
        week_plan = []
        
        for r_dict in filtered_resources:
            r = r_dict['resource']
            
            if r.id in used_resource_ids:
                continue
                
            est_hours = r.estimated_hours if r.estimated_hours else 1.0
            
            if week_hours + est_hours <= available_hours_per_week:
                week_plan.append({
                    "id": r.id,
                    "title": r.title,
                    "url": r.url,
                    "type": r.resource_type,
                    "difficulty": r.difficulty_level,
                    "quality_score": r.quality_score,
                    "estimated_hours": est_hours,
                    "relevance_score": r_dict['similarity_score']
                })
                week_hours += est_hours
                used_resource_ids.add(r.id)
                
            if week_hours >= available_hours_per_week * 0.8: # Allow 80% fill to be considered "full"
                break
                
        if week_plan:
            plan.append({
                "week": current_week,
                "total_hours": week_hours,
                "resources": week_plan
            })
        
        current_week += 1
        
    return plan
