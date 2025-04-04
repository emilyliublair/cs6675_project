"use client";

import { Post } from "@/@types/type";
import { Dispatch, SetStateAction, useState } from "react";

type PostFormProps = {
  posts: Post[];
  setPosts: Dispatch<SetStateAction<Post[]>>;
  toggleView: () => void;
};

export default function PostForm({
  posts,
  setPosts,
  toggleView,
}: PostFormProps) {
  const [formData, setFormData] = useState<{
    name: string;
    title: string;
    description: string;
  }>({
    name: "",
    title: "",
    description: "",
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const newPost: Post = {
      ...formData,
      publishDate: new Date(),
    };
    setPosts([...posts, newPost]);
    toggleView();
  };

  const handleChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>
  ) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }));
  };

  const handleCancel = () => {
    setFormData({ name: "", title: "", description: "" });
    toggleView();
  };

  return (
    <div className="card mb-6">
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label
            htmlFor="name"
            className="block text-sm font-medium text-gray-700 mb-1"
          >
            Your Name
          </label>
          <input
            type="text"
            id="name"
            name="name"
            value={formData.name}
            onChange={handleChange}
            className="input-field"
            placeholder="Enter your name"
            required
          />
        </div>

        <div>
          <label
            htmlFor="title"
            className="block text-sm font-medium text-gray-700 mb-1"
          >
            Question Title
          </label>
          <input
            type="text"
            id="title"
            name="title"
            value={formData.title}
            onChange={handleChange}
            className="input-field"
            placeholder="Enter your question title"
            required
          />
        </div>

        <div>
          <label
            htmlFor="description"
            className="block text-sm font-medium text-gray-700 mb-1"
          >
            Question Description
          </label>
          <textarea
            id="description"
            name="description"
            value={formData.description}
            onChange={handleChange}
            className="input-field min-h-[150px] resize-y"
            placeholder="Describe your question in detail..."
            required
          />
        </div>

        <div className="flex justify-end space-x-3">
          <button
            type="button"
            className="btn-secondary hover:cursor-pointer"
            onClick={handleCancel}
          >
            Cancel
          </button>
          <button
            type="submit"
            className="btn-primary hover:cursor-pointer"
            onClick={handleSubmit}
          >
            Post Question
          </button>
        </div>
      </form>
    </div>
  );
}
