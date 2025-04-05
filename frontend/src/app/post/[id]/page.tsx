"use client";

import { Answer, Post } from "@/@types/type";
import AnswerCard from "@/components/AnswerCard";
import QuestionCard from "@/components/QuestionCard";
import { fetchPost } from "@/utils/api";
import { useEffect, useState } from "react";

type PostDetail = {
  post: Post;
  answer: Answer;
};

export default function PostDetails({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const [postDetail, setPostDetail] = useState<PostDetail | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const loadPost = async () => {
      try {
        setIsLoading(true);
        const { id } = await params;
        console.log(id);
        const data = await fetchPost(id);
        setPostDetail(data);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Failed to load post");
      } finally {
        setIsLoading(false);
      }
    };

    loadPost();
  }, [params]);

  if (isLoading) {
    return <div className="text-center py-8">Loading post...</div>;
  }

  if (error) {
    return <div className="text-center py-8 text-red-500">Error: {error}</div>;
  }

  if (!postDetail) {
    return <div className="text-center py-8">Post not found</div>;
  }

  return (
    <div className="max-w-4xl mx-auto p-6">
      <QuestionCard {...postDetail.post} />

      <AnswerCard {...postDetail.answer} />
    </div>
  );
}
