from typing import TypedDict, List, Optional

class YouTubeSearchSnippet(TypedDict):
    publishedAt: str
    channelId: str
    title: str
    description: str
    channelTitle: str

class YouTubeSearchId(TypedDict):
    kind: str
    videoId: Optional[str]

class YouTubeSearchResult(TypedDict):
    id: YouTubeSearchId
    snippet: YouTubeSearchSnippet

class YouTubeSearchResponse(TypedDict):
    items: List[YouTubeSearchResult]

class YouTubeVideoContentDetails(TypedDict):
    duration: str
    caption: str

class YouTubeVideoStatistics(TypedDict):
    viewCount: Optional[str]
    likeCount: Optional[str]
    commentCount: Optional[str]

class YouTubeVideoSnippet(TypedDict):
    publishedAt: str
    channelId: str
    title: str
    description: str
    channelTitle: str
    defaultAudioLanguage: Optional[str]

class YouTubeVideoResult(TypedDict):
    id: str
    snippet: YouTubeVideoSnippet
    contentDetails: YouTubeVideoContentDetails
    statistics: YouTubeVideoStatistics

class YouTubeVideoResponse(TypedDict):
    items: List[YouTubeVideoResult]

class YouTubeCommentSnippet(TypedDict):
    videoId: str
    textDisplay: str
    textOriginal: str
    authorDisplayName: str
    likeCount: int
    publishedAt: str
    updatedAt: str

class YouTubeTopLevelComment(TypedDict):
    snippet: YouTubeCommentSnippet

class YouTubeCommentThreadSnippet(TypedDict):
    videoId: str
    topLevelComment: YouTubeTopLevelComment
    canReply: bool
    totalReplyCount: int

class YouTubeCommentThreadResult(TypedDict):
    id: str
    snippet: YouTubeCommentThreadSnippet

class YouTubeCommentThreadResponse(TypedDict):
    items: List[YouTubeCommentThreadResult]
    nextPageToken: Optional[str]
