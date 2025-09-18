import yaml

input_path = "assets/unified_dataset/combined_concat.yaml"
output_path = "assets/unified_dataset/combined_concat_padded.yaml"

with open(input_path, "r") as f:
    data = yaml.safe_load(f)

names = data["names"]

# Build new names dict with placeholders
new_names = {}
new_names[0] = names[0]  # person

# Insert placeholders for 1-66
for i in range(1, 67):
    new_names[i] = ""

# Add the rest of the original classes
for k in sorted(names.keys()):
    if k > 0:
        new_names[k] = names[k]

# Update and write out
data["names"] = new_names

with open(output_path, "w") as f:
    yaml.dump(data, f, sort_keys=False)

print(f"Updated YAML written to {output_path}")