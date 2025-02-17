models = [
    "hr_performance",
    "hr_performance_problem",
    "hr_performance_note",
    "hr_performance_goals",
    "hr_res_performance",
    "res_company",
    "res_users",
    "hr_performance_comms",
    "hr_performance_product_work",
    "hr_performance_computer_skills",
    "hr_performance_profession",
    "hr_performance_team",
    "hr_performance_firm",
]

csv_content = "id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink\n"
for model in models:
    csv_content += f"access_{model},HR {model.replace('_', ' ').title()},model_{model},scidar_review.group_hr_performance_manager,1,1,1,1\n"

with open("security/ir.model.access.csv", "w") as f:
    f.write(csv_content)

print("✅ ir.model.access.csv generated successfully!")
