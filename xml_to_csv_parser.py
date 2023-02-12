import csv
import html
import re
import xml.etree.ElementTree as ET

INPUT_XML_FILE = 'out.txt'
OUTPUT_CSV_FILE = 'output.csv'

CSV_HEADER = ['url', 'title', 'updated', 'comment_title', 'content', 'id', 'author', 'link']

with open(OUTPUT_CSV_FILE, 'w') as fout:
    csv_writer = csv.writer(fout, quotechar='"')
    csv_writer.writerow(CSV_HEADER)

    with open(INPUT_XML_FILE, 'r', encoding='utf-16') as fin:
        for line in fin:
            # The input xml file consists of two columns which are formatted like this: URL,"""XML_CODE"""
            # The XML_CODE column can appear in two different formats:
            # 1) <html><head></head><body><pre ... ><?xml version="1.0" ... </feed></pre></body></html>
            # 2) <?xml version="1.0" ... </feed>
            # We will use re.search() the extract the XML code (starting with <?xml ...)
            url = line.split(',"""')[0]
            xmlstring = line.split('"""')[1]
            xmlstring = html.unescape(xmlstring)
            mo = re.search(r'\<\?xml version=.+\</feed\>', xmlstring)
            xmlstring = mo.group()

            tree = ET.ElementTree(ET.fromstring(xmlstring))
            root = tree.getroot()

            title = root.find('{http://www.w3.org/2005/Atom}title').text

            # A reddit post consists of multiple comments/entries. We need to iterate over them.
            entries = root.findall('{http://www.w3.org/2005/Atom}entry')

            for entry in entries:
                # Deleted comments do not have the author/name child
                author_element = entry.find('{http://www.w3.org/2005/Atom}author')
                if author_element:
                    entry_author = author_element.find('{http://www.w3.org/2005/Atom}name').text
                else:
                    entry_author = '[deleted]'

                entry_title = entry.find('{http://www.w3.org/2005/Atom}title').text
                entry_updated = entry.find('{http://www.w3.org/2005/Atom}updated').text
                entry_id = entry.find('{http://www.w3.org/2005/Atom}id').text
                entry_link = entry.find('{http://www.w3.org/2005/Atom}link').attrib['href']

                entry_content_child = entry.find('{http://www.w3.org/2005/Atom}content')
                if entry_content_child.text:
                    # Most content elements have simply text based
                    entry_content = entry_content_child.text
                else:
                    # Some other content elements are more complex and can be entire HTML tables
                    entry_content = ET.tostring(entry_content_child, encoding='unicode')
                # The content can have multiple HTML tags like <div> and <p>. We want to remove them.
                entry_content = re.sub(r'<[^>]+>', '', entry_content)
                entry_content = html.unescape(entry_content)
                entry_content = entry_content.strip()

                csv_writer.writerow([url, title, entry_updated, entry_title, entry_content, entry_id, entry_author, entry_link])

    #        for child in root:
    #            print(f"{child.tag} ### {child.attrib} ### {child.text}")
    #            if child.tag.endswith('}entry'):
    #                pass
                    #print(child.)
