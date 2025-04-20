"use client";

import { Post } from "@/@types/type";
import TeacherAnswerCard from "@/components/TeacherAnswerCard";
import QuestionCard from "@/components/QuestionCard";
import { fetchPosts } from "@/utils/api";
import { useEffect, useState } from "react";

export default function TeacherView() {
  const [posts, setPosts] = useState<Post[]>([]);
  const [selectedPost, setSelectedPost] = useState<Post | null>(null);
  const [answer, setAnswer] = useState<any>(null);

  useEffect(() => {
    const loadPosts = async () => {
      try {
        const fetchedPosts = await fetchPosts();
        setPosts(fetchedPosts);
      } catch (err) {
        console.error("Error loading posts:", err);
      }
    };

    loadPosts();
  }, []);

  const handlePostClick = async (post: Post) => {
    try {
      const response = await fetch(`http://localhost:8001/post/${post._id}`);
      if (response.ok) {
        const data = await response.json();
        setSelectedPost(post);
        setAnswer(data.answer);
      }
    } catch (error) {
      console.error("Error fetching post details:", error);
    }
  };

  return (
    <div className="max-w-7xl mx-auto p-6">
      <h1 className="text-2xl font-bold text-gray-800 mb-6">Teacher Dashboard</h1>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div>
          <h2 className="text-xl font-semibold text-gray-700 mb-4">Questions</h2>
          <div className="space-y-4">
            {posts.map((post) => (
              <div
                key={post._id}
                onClick={() => handlePostClick(post)}
                className={`cursor-pointer ${
                  selectedPost?._id === post._id ? "ring-2 ring-blue-500" : ""
                }`}
              >
                <QuestionCard {...post} />
              </div>
            ))}
          </div>
        </div>

        <div>
          <h2 className="text-xl font-semibold text-gray-700 mb-4">Answer</h2>
          {selectedPost && answer ? (
            <TeacherAnswerCard answer={answer} />
          ) : (
            <div className="text-gray-500 text-center py-8">
              Select a question to view and edit its answer
            </div>
          )}
        </div>
      </div>
    </div>
  );
} 