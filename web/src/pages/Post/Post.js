import React, {useEffect, useState} from 'react'
import {useLocation} from "react-router-dom";
import PostComponent from "../../components/Post/Post";
import NewPost from "../../components/NewPost/NewPost";
import './Post.css'

export default (props) => {
  const [loading, updateLoading] = useState(true)
  const [post, updatePost] = useState(null)
  const [me, updateMe] = useState(null)
  const [resharePost, updateResharePost] = useState(null)
  const [newPostOpened, updateNewPostOpened] = useState(false)

  useEffect(async () => {
    updateMe(await props.api.getMe())
    updatePost(await props.api.getPost(props.postId))
    updateLoading(false)
  }, [])

  let highlightCommentId
  const location = useLocation()
  if (location.hash) {
    highlightCommentId = location.hash.split('#comment-')[1]
  }

  const renderPost = () => {
    if (loading) {
      return (<div className="post-status">Loading...</div>)
    }
    if (!post) {
      return (<div className="post-status">Errored loading post</div>)
    }
    return (
      <>
        <PostComponent
          detail={true}
          hasNewPostModal={true}
          data={post}
          highlightCommentId={highlightCommentId}
          me={me}
          api={props.api}
          disableNavigateToPostPage={true}
          resharePostData={resharePost}
          updateResharePostData={updateResharePostData}
          updateNewPostOpened={updateMobileNewPostOpened}
        />
        {newPostOpened &&
          <div id="post-new-post-modal" className="post-detail-new-post-modal">
            <div className="post-detail-new-post-modal-content">
              <NewPost
                api={props.api}
                resharePostData={resharePost}
                updateResharePostData={updateResharePostData}
                beforePosting={() => {
                  updateMobileNewPostOpened(false)
                }}
                afterPosting={() => {}}
              />
            </div>
          </div>
        }
      </>
    )
  }

  window.onclick = (event) => {
    let modal = document.getElementById("post-new-post-modal");
    if (event.target === modal) {
      updateNewPostOpened(false)
    }
  }

  const updateResharePostData = (data) => {
    updateResharePost(data)
  }
  const updateMobileNewPostOpened = (opened) => {
    updateNewPostOpened(opened)
  }

  return (
    <div className='post-wrapper-page'>
      {renderPost()}
    </div>
  )
}
