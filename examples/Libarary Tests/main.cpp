#include <iostream>
#include <vulkan/vulkan.h>
#include <vulkan_wrapper.h>
#include <glfw/glfw3.h>
#define TINYOBJLOADER_IMPLEMENTATION
#include <glm/glm.hpp>
#define STB_IMAGE_IMPLEMENTATION
#include <stb_image.h>
#include <gli/gli.hpp>
#include <assimp/Importer.hpp>
#include <assimp/scene.h>    
#include <assimp/postprocess.h>


std::string dataPath = "../data/";
std::string modelPath = dataPath + "Models/";
std::string texturePath = dataPath + "Textures/";
std::string shaderPath = dataPath + "Shader/";


class GlfwWindow : public vkw::Window {
public:
	GlfwWindow(int x, int y) : vkw::Window(*this)
	{
		glfwInit();
		glfwWindowHint(GLFW_CLIENT_API, GLFW_NO_API);
		glfwWindowHint(GLFW_RESIZABLE, GLFW_FALSE);
		window = glfwCreateWindow(x, y, "Vulkan", nullptr, nullptr);
	}

	~GlfwWindow() override {
		glfwDestroyWindow((GLFWwindow*)window);
	};

	void createSurface(VkInstance instance, VkSurfaceKHR * surface) const override {
		vkw::Debug::errorCodeCheck(glfwCreateWindowSurface(instance, (GLFWwindow*)window, nullptr, surface), "Failed to create Surface");
	};

	static void getWindowExtensions(std::vector<const char*> & ext) {
		unsigned int glfwExtensionCount = 0;
		const char** glfwExtensions;
		glfwExtensions = glfwGetRequiredInstanceExtensions(&glfwExtensionCount);

		for (unsigned int i = 0; i < glfwExtensionCount; i++) {
			ext.push_back(glfwExtensions[i]);
		}
	};

	void getWindowSize(int * width, int * height) const override {
		glfwGetWindowSize((GLFWwindow*)window, width, height);
	};
};

struct foo {
	~foo() {
		int i = 5;
	}
};


int main() {
	foo f;

	// glfw test
	GlfwWindow window = GlfwWindow(800, 600);


	// Vulkan Wraper test
	vkw::Instance::CreateInfo instanceCreateInfo = {};
	GlfwWindow::getWindowExtensions(instanceCreateInfo.desiredExtensions);
	
	vkw::Instance instance(instanceCreateInfo);


	// stb test
	int texWidth, texHeight, texChannels;
	std::string path = texturePath + "picture.png";
	stbi_uc * pixels = stbi_load(path.c_str(), &texWidth, &texHeight, &texChannels, STBI_rgb_alpha);
	std::cout << "stb test successful" << std::endl;



	// glm test
	glm::mat4 matrix;
	glm::vec4 vec;
	auto test = matrix * vec;
	std::cout << "glm test successful" << std::endl;


	
	// gli test
	gli::texture_cube texCube(gli::load(texturePath + "cubemap_yokohama_bc3_unorm.ktx"));
	assert(!texCube.empty());
	std::cout << "gli test successful" << std::endl; 



	// assimp test
	Assimp::Importer importer;
	const aiScene * scene = importer.ReadFile(modelPath + "Teapot.obj",
		aiProcess_CalcTangentSpace |
		aiProcess_Triangulate |
		aiProcess_JoinIdenticalVertices |
		aiProcess_SortByPType);

	if (!scene) {
		std::cout << importer.GetErrorString() << std::endl;
		exit(-1);
	}
	std::cout << "assimp test successful" << std::endl;


	getchar();

	window.~GlfwWindow();
	glfwTerminate();
}