Here is my plan for a small project:

There is a guide, The Omarchy Manual, that has a few chapters to read (36). I want a script that, from a static base-url:

1. Fetches the base url and finds links for all the chapters. The query parameter of this should be static, as a global constant.
2. Fetches the contents of these pages and extracts only the contents of the <main> element of the page.
3. Convert this extracted HTML to Markdown.
3.a. Save the Markdown to a corresponding file in a directory.
4. Join all these chapters together to one, big, Markdown file.
4.a. Save this big Markdown file to disk.

One thing to note: I would like for the script to tell me whether the contents of any of the chapters have changed since the last time I ran the script. This should probably be done by comparing the current contents with a previously saved version.

Another thing to note: I like progress bars! If possible, please include progress bars for the fetching and conversion steps. If you do anything in parallel, please make sure the progress bars still work.