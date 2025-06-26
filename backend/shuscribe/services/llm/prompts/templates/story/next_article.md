Okay, let's write this article:
<Article title="Pallet Town" file="wiki/locations/Pallet_Town.md"/>

<ArticlePlan title="Pallet Town" type="LOCATION">
<RestrictChapters>
    <Chapter file="story/chapter11.txt"/>
    <Chapter file="story/chapter12.txt"/>
    <Chapter file="story/chapter13.txt"/>
    <Chapter file="story/chapter14.txt"/>
    <Chapter file="story/chapter15.txt"/>
</RestrictChapters>
<Tools>
    <InternetSearch query="Pallet Town Kanto map Professor Oak Ash Ketchum home"/>
</Tools>
<Structure>
# Overview
# Geography and Layout
    ## Location relative to Viridian City
    ## Key Buildings (Oak's Lab, Ketchum House, other residences)
    ## Surrounding Environment (Forest paths, hills)
# Key Locations within Pallet Town
    ## Ketchum Household
    ## Professor Oak's Laboratory
    ## Forest Path (Site of Stephen's murder)
# Inhabitants
    ## Ketchum Family (Delia, Ash, Stephen)
    ## Professor Oak
# Plot Relevance
    ## Destination for Dr. Fuji and Amber
    ## Site of Confrontation and Murder
    ## Temporary Home for Amber
    ## Setting for Final Battle (Chapters 14-15)
</Structure>
</ArticlePlan>

# Specifications

## Instructions

Before you write the article, make sure you understand and know what goes into a good wiki article page, and specifically how detailed you want this particular article to be. Is there anything about the structure of this wiki that should be changed? If there is, don't be afraid to make the change, but make you sure let me know by adding a separate block specifically for the updated article plan change:

```xml
<ArticlePlan>
...
</ArticlePlan>
```

## Format

Use the following format:

```xml
<Article title="Article Title" type="article_type" file="wiki/path/to/Article Title.md">
<Preview>
<!-- Short blurb preview of the article to be displayed on hover for a tooltip to the article in Markdown (not commented) -->
This should be either a short blurb paraphrasing everything in the article (not describing what the article is, but describing the actual content), or a discrete fields for entity-type articles (mixture of a blurb and markdown table or bullet points).

</Preview>
<Content>
<!-- Markdown Content of the wiki article -->
</Content>
</Article>
```

## Link Format

Remember to use appropriate markdown link syntax throughout. However, try to be liberal with them, too many links is annoying and bad UX.
- Link to another article: [Article Title Display](wiki/path/to/Article%20Title.md)
- Link to another article's H2 Header (## H2 Header): [Display Alias (link)](wiki/path/to/Article@20Title.md#h2-header)
- Link to section within the article: [Display Alias (link)](#section-name)
- Link to external website: [display link](https://link-url-here.org)

Note that if we link to another article, it must never start with `#` (these are only for sections within the same article)

Additionally, add metadata to the article links to describe the relationship between 

ALL LINKS should use the markdown link format: [display](link)
