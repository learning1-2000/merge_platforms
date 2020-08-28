#coding=utf-8
from django.contrib import admin

from yt.models import YoutubeAccount, YoutubeVideo, YoutubeComment

# 账号
class YoutubeAccountAdmin(admin.ModelAdmin):
	list_display = ('ytid', 'name', 'home_url')

admin.site.register(YoutubeAccount, YoutubeAccountAdmin)

# 视频
class YoutubeVideoAdmin(admin.ModelAdmin):
	list_display = ('ytid', 'title',"watch_count","comment_count", 'url')

admin.site.register(YoutubeVideo, YoutubeVideoAdmin)

# 评论
class YoutubeCommentAdmin(admin.ModelAdmin):
	list_display = ('video',"commenter_name","comment_content","up_count" )

admin.site.register(YoutubeComment, YoutubeCommentAdmin)