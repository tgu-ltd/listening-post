import subprocess
import json

def line_to_json(line):
    l = []
    for s in line.split(' '):
        if s:
            l.append(s.strip())

    return {
        'name': l[0],
        'activity': l[1],
        'state': l[3],
        'description': ' '.join(l[4:])
    }


def get_services_status():
    # Run `systemctl` command to get all service statuses
    result = subprocess.run(
        ["systemctl", "list-units", "--type=service", "--all"],
        stdout=subprocess.PIPE,
        text=True
    )
    
    # Parse the output
    services = {'loaded': []}
    for line in result.stdout.splitlines():
        if "loaded" in line:
            service = line_to_json(line)
            if service.get('name') == 'LOAD':
                break
            services['loaded'].append(service)
    return services


def main():
    # Get service statuses
    services_status = get_services_status()
    
    # Convert to JSON and print
    print(json.dumps(services_status, indent=4))

if __name__ == "__main__":
    main()