# Update these IDs to control access
# Use SRNs or PESU email IDs (case-insensitive)
SUPERADMIN_IDS = {
    "PES1UG25CS527",
}

# Map class_id -> set of CR SRNs/emails
# class_id format: <Program>-<Branch>-Sem<Semester>-<Section>
# Example: "BTech-CSE-Sem2-A"
# If branch isn't assigned (common first-year), branch may be empty,
# which yields a double hyphen like: "BTech--Sem1-C9".
CR_IDS_BY_CLASS = {
    # "BTech-CSE-Sem2-A": {"SRN123", "cr@pesu.pes.edu"},
    "BachelorofTechnology--Sem2-SectionC9": {"PES1UG25CS527"},
    
}
