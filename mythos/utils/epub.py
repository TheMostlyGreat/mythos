import os
from ebooklib import epub
import markdown
from mythos.story import Story

def create_epub(story: Story):
    """
    Assembles an EPUB book from a Story object.

    :param story: The Story object containing manuscript chapters.
    """
    # Set EPUB metadata from Story
    title = story.title or "Untitled"
    identifier = story.story_id
    language = "en"  # Default language

    # Define the EPUB output path based on the story directory and title
    epub_path = story.story_dir / f"{title}.epub"

    # Initialize the EPUB book
    book = epub.EpubBook()

    # Set metadata for the EPUB book
    book.set_identifier(identifier)
    book.set_title(title)
    book.set_language(language)

    chapters = []
    toc = []

    # Iterate over each chapter in the manuscript
    for chapter_name, story_asset in story.manuscript.items():
        md_content = story_asset.details
        
        # Convert Markdown content to HTML
        try:
            html_content = markdown.markdown(md_content, extensions=['toc', 'fenced_code'])
        except Exception as e:
            raise Exception(f"Markdown conversion failed for {story_asset.relative_file_path}: {e}")

        # Create an EPUB chapter with the converted HTML content
        chapter = epub.EpubHtml(
            title=story_asset.title,
            file_name=f"{chapter_name}.xhtml",
            lang=language
        )
        chapter.content = html_content
        book.add_item(chapter)
        chapters.append(chapter)

        # Add the chapter to the table of contents
        toc.append(epub.Link(f"{chapter_name}.xhtml", story_asset.title, chapter_name))

    # Define the Table of Contents for the EPUB book
    book.toc = tuple(toc)

    # Add default NCX and Nav files for navigation
    book.add_item(epub.EpubNcx())
    book.add_item(epub.EpubNav())

    # Define CSS styles 
    css_content = 'body { font-family: Georgia, serif; }'  # Updated font-family
    nav_css = epub.EpubItem(
        uid="style_nav",
        file_name="style/nav.css",
        media_type="text/css",
        content=css_content.encode('utf-8')  # Ensure bytes
    )
    book.add_item(nav_css)

    # Set the spine of the EPUB (the reading order)
    book.spine = ['nav'] + chapters

    # Link the CSS stylesheet to all HTML chapters
    for item in book.get_items():
        if isinstance(item, epub.EpubHtml):
            item.add_link(
                href='style/nav.css',
                rel='stylesheet',
                type='text/css'
            )

    # Ensure the output directory exists; create it if it doesn't
    output_dir = os.path.dirname(epub_path)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Write the EPUB file to the specified path
    try:
        epub.write_epub(epub_path, book, {})
        print(f"EPUB file created successfully at {epub_path}")
    except Exception as e:
        raise Exception(f"Failed to write EPUB file: {e}")
