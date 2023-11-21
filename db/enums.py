import enum


class Visibility(str, enum.Enum):
    public = "public"
    private = "private"
    draft = "draft"


class UrlType(str, enum.Enum):
    youtube = "youtube"
    soundcloud = "soundcloud"
    github = "github"
    sketchfab = "sketchfab"
    unityroom = "unityroom"
    other = "other"


class AssetType(str, enum.Enum):
    zip = "zip"
    image = "image"
    video = "video"
    music = "music"
    model = "model"


class BlogAssetType(str, enum.Enum):
    image = "image"
    video = "video"
