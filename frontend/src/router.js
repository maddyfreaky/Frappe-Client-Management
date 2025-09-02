import { userResource } from "@/data/user"
import { createRouter, createWebHistory } from "vue-router"
import { session } from "./data/session"
import Sidebarlayout from "@/Layouts/SidebarLayout.vue"

const routes = [
	{
		path:"/",
		component: Sidebarlayout,
		children:[
	{
		path: "",
		name: "Home",
		component: () => import("@/pages/Home.vue"),
	},
	
	{
		name: "Template",
		path: "/template",
		component: () => import("@/pages/TemplateCreation.vue"),
	},
	{
		name: "Template Tasks",
		path: "/templatetasks",
		component: () => import("@/pages/TemplateTasks.vue"),
	},
	{
		name: "TemplateEditor",
		path: '/templates/:name/edit',
		component: () => import("@/pages/TemplateEditor.vue"),
		props: true
	},
	{
		name: "Client Creation",
		path: "/clientcreation",
		component: () => import("@/pages/ClientForm.vue"),
	},
	{
		name: "ActivityForm",
		path: '/assign-template/:templateName',
		component: () => import("@/pages/ActivityForm.vue"),
	},
	{
		name: 'ActivityList',
		path: '/activities',
		component: () => import("@/pages/ActivityList.vue"),
		meta: { requiresAuth: true }
	},
	{
		name: 'ActivityDetail',
		path: '/activities/:activityName',
		component: () => import("@/pages/ActivityDetail.vue"),
		meta: { requiresAuth: true }
	},
	{
		name: 'UserTasks',
		path: '/usertasks',
		component: () => import("@/pages/UserTasks.vue"),
		meta: { requiresAuth: true }
	},
	{
		name: "TaskDetail",
		path: '/tasks/:id',
		component: () => import("@/pages/TaskDetailPage.vue"),
		props: true
	},
	{
        path: "frontend/edit-client/:name",
        name: "EditClientFile",
        component: () => import("@/pages/EditClientFile.vue"),
        props: true
    },
]
},
	{
		name: "Login",
		path: "/account/login",
		component: () => import("@/pages/Login.vue"),
	},
]

const router = createRouter({
	history: createWebHistory("/frontend"),
	routes,
})

router.beforeEach(async (to, from, next) => {
	let isLoggedIn = session.isLoggedIn
	try {
		await userResource.promise
	} catch (error) {
		isLoggedIn = false
	}

	if (to.name === "Login" && isLoggedIn) {
		next({ name: "Home" })
	} else if (to.name !== "Login" && !isLoggedIn) {
		next({ name: "Login" })
	} else {
		next()
	}
})

export default router
