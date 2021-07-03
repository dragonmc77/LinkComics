# LinkComics
Link the comics in your library in a separate folder structure.

USE CASE:
I use Calibre to manage my comic book library of 60,000+ comics. While it is great at management, serving the books up via the built-in web server is a poor experience, due to the focus on ebooks rather than comics. The problem is that ebook management is centered around <b>authors</b>, while comic management is centered around <b>series</b>. I personally prefer Komga as my comic book server of choice, but you can't simply import your Calibre library into Komga because Calibre has one (rigid) way of storing the files, and Komga expects another. There are ways around this that involve different approaches. My idea was to simply make links to all my comics in a separate folder structure determined by comic metadata. The folder structure would be friendly to Komga, so it would have no trouble presenting the comics to the user as one would logically expect. This project does this automatically for your entire comic library. 

DETAILS:<br>
Reads the metadata in each comic book file in a given location and places a link to that file in another location, within a specific folder structure based on the metadata.

Example:<br>
Let's say your library is in /home/user/comics, and you choose to put the links in /home/user/comic_links.<br>
    The script will read the metadata for all comic files in /home/user/comics and create links in /home/user/comic_links with the following structure:<br>
    /home/user/comic_links/<i>Publisher</i>/<i>Series</i>/<i>Volume</i>/<i>Series #000 (Year-Month).cbz</i><br>
    i.e., a link would be:<br>
    /home/user/comic_links/Marvel/X-Men/V2013/X-Men #012 (2014-05).cbz

This separate folder structure containing links could then be imported into any services that expect a set folder structure, such as Komga or Ubooquity.