import { Answer, Post } from "@/@types/type";

const API_URL = "http://localhost:8001";

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

export const createPost = async (
  post: Omit<Post, "publishDate">
): Promise<Post> => {
  try {
    const response = await fetch(`${API_URL}/posts`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Access-Control-Allow-Credentials": "*",
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

export const fetchPost = async (
  id: string
): Promise<{ post: Post; answer: string }> => {
  try {
    const response = await fetch(`${API_URL}/post/${id}`);
    if (!response.ok) {
      throw new Error("Failed to fetch post");
    }
    return await response.json();
  } catch (error) {
    console.error("Error fetching post:", error);
    throw error;
  }
};
