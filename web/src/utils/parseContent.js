import React from 'react';

export default (content, className) => {
  const regExForStrikeThrough = /(^|\s)-(.+?)-($|\s)/gm
  const regExForItalic = /(^|\s)_(.+?)_($|\s)/gm
  const regExForBold = /(^|\s)\*(.+?)\*($|\s)/gm
  const regExForMention = /@([A-Za-z0-9_-]+)(\s|$)/gm;
  // https://stackoverflow.com/questions/3809401/what-is-a-good-regular-expression-to-match-a-url
  const regExForUrl = /(https?:\/\/(www\.)?[-a-zA-Z0-9@:%._+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_+.~#?&//=]*))/g

  const newContent = content
    .replace(regExForStrikeThrough, '$1<del>$2</del>$3')
    .replace(regExForItalic, '$1<i>$2</i>$3')
    .replace(regExForBold, '$1<b>$2</b>$3')
    .replace(
      regExForMention,
      // TODO: this triggers a reload still #167
      `<a href="/profile/$1" style="color: #56a5ff; text-decoration: none;">@$1</a>$2`
    )
    .replace(
        regExForUrl,
        `<a href="$1" style="color: #56a5ff; text-decoration: none;" target="_blank" rel="noreferrer noopener">$1</a>`
    )

  return <div className={className} dangerouslySetInnerHTML={{__html: newContent}}/>
}
