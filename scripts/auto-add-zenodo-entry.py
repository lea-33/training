# This script is executed when a new issue is created on our github repository. 
# In case the issue text consists only of a single line starting like a zenodo link, 
# it will retrieve all important details from the zenodo record, add it to a yml file
# and send a pull-request
import sys
from _github_utilities import create_branch, get_file_in_repository, get_issue_body, write_file, send_pull_request
import yaml


def main():
    repository = sys.argv[1]
    issue = int(sys.argv[2])
    
    yml_filename = "resources/nfdi4bioimage.yml"
    
    
    issue_text = get_issue_body(repository, issue)
    if "\n" in issue_text or not issue_text.startswith("https://zenodo.org/records"):
        print(issue_text, " is not a zenodo link. I show myself out.")
        return

    zenodo_url = issue_text
    
    # read data from zenodo
    zenodo_data_dict = complete_zenodo_data(zenodo_url)
    zenodo_yml = "\n- " + yaml.dump(zenodo_data_dict).replace("\n", "\n  ")

    # read "database"
    branch = create_branch(repository)
    file_content = get_file_in_repository(repository, branch, yml_filename).decoded_content.decode()
    
    print("yml file content length:", len(file_content))

    # add entry
    file_content += zenodo_yml
    file_content

    # save back to github
    write_file(repository, branch, yml_filename, file_content, "Add " + zenodo_url)
    res = send_pull_request(repository, branch, "Add " + zenodo_url, f"closes #{issue}") 

    print("Done.", res)
    

def complete_zenodo_data(zenodo_url):
    from generate_link_lists import read_zenodo, remove_html_tags
    zenodo_data = read_zenodo(zenodo_url)
    entry = {}
    urls = [zenodo_url]

    if 'doi_url' in zenodo_data.keys():
        doi_url = zenodo_data['doi_url']
        
        # Add DOI URL to the URLs list if it's not already there
        if doi_url not in urls:
            urls.append(doi_url)
    entry['url'] = urls
        
    if 'metadata' in zenodo_data.keys():
        metadata = zenodo_data['metadata']
        # Update entry with Zenodo metadata and statistics
        entry['name'] = metadata['title']
        if 'publication_date' in metadata.keys():
            entry['publication_date'] = metadata['publication_date']
        if 'description' in metadata.keys():
            entry['description'] = remove_html_tags(metadata['description'])
        if 'creators' in metadata.keys():
            creators = metadata['creators']
            entry['authors'] = ", ".join([c['name'] for c in creators])
        if 'license' in metadata.keys():
            entry['license'] = metadata['license']['id']
    
    if 'stats'  in zenodo_data.keys():
        entry['num_downloads'] = zenodo_data['stats']['downloads']

    return entry


if __name__ == "__main__":
    main()

