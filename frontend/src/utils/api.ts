import { Post } from "@/@types/type";

const API_URL = "http://localhost:8000";

export const fetchPosts = async (): Promise<Post[]> => {
  try {
    const response = await fetch(`${API_URL}/posts`);
    if (!response.ok) {
      throw new Error("Failed to fetch posts");
    }
    return await response.json();
  } catch (error) {
    console.error("Error fetching posts:", error);
    throw error;
  }
};

export const createPost = async (post: Omit<Post, "publishDate">): Promise<Post> => {
  try {
    const response = await fetch(`${API_URL}/posts`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(post),
    });
    if (!response.ok) {
      throw new Error("Failed to create post");
    }
    return await response.json();
  } catch (error) {
    console.error("Error creating post:", error);
    throw error;
  }
}; 