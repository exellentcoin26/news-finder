-- CreateTable
CREATE TABLE "NewsSources" (
    "id" SERIAL NOT NULL,
    "name" TEXT NOT NULL,
    "url" TEXT NOT NULL,

    CONSTRAINT "NewsSources_pkey" PRIMARY KEY ("id")
);

-- CreateIndex
CREATE UNIQUE INDEX "NewsSources_name_key" ON "NewsSources"("name");

-- CreateIndex
CREATE UNIQUE INDEX "NewsSources_url_key" ON "NewsSources"("url");
