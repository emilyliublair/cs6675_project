"use client";

import { Post } from "@/@types/type";
import PostForm from "@/components/PostForm";
import QuestionCard from "@/components/QuestionCard";
import { fetchPosts } from "@/utils/api";
import { Plus } from "lucide-react";
import { Suspense, useEffect, useState } from "react";

const Home = () => {
  const [showAddPost, setShowAddPost] = useState<boolean>(false);
  const [posts, setPosts] = useState<Post[]>([]);

  useEffect(() => {
    const loadPosts = async () => {
      try {
        const fetchedPosts = await fetchPosts();
        setPosts(fetchedPosts);
        console.log(fetchedPosts);
      } catch (err) {
        console.log(err);
      }
    };

    loadPosts();
  }, []);

  const toggleAddView = () => {
    setShowAddPost(!showAddPost);
  };
  return (
    <div className="max-w-4xl mx-auto">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold text-gray-800">Recent Questions</h1>
        <button
          className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 hover:cursor-pointer flex items-center space-x-2"
          onClick={toggleAddView}
        >
          <Plus className="" /> <span>New Question</span>
        </button>
      </div>
      {showAddPost && <PostForm toggleView={toggleAddView} />}
      <div className="space-y-4">
        {posts.map((currPost: Post, idx: number) => {
          return <div     onClick={() => {
            window.location.href = `/post/${currPost._id}`;
          }}><QuestionCard key={idx} {...currPost} /></div>;
        })}
      </div>
    </div>
  );
};

const SuspenseHome = () => {
  return (
    <Suspense fallback={<div>Loading...</div>}>
      <Home></Home>
    </Suspense>
  );
};

export default SuspenseHome;
